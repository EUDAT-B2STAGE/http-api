# -*- coding: utf-8 -*-

import os
import hashlib
import zipfile
import re
import requests
from shutil import rmtree
from socket import gethostname
from plumbum.commands.processes import ProcessExecutionError

from b2stage.apis.commons.b2handle import PIDgenerator, b2handle
from seadata.apis.commons.queue import prepare_message
from seadata.apis.commons.seadatacloud import Metadata as md, ImportManagerAPI
from seadata.apis.commons.seadatacloud import ErrorCodes
from seadata.apis.commons.seadatacloud import seadata_vars

from restapi.flask_ext.flask_celery import CeleryExt
from restapi.flask_ext.flask_irods.client import IrodsException
from restapi.services.detect import detector
from restapi.flask_ext.flask_celery import send_errors_by_email

from utilities.basher import BashCommands
from utilities import path
from utilities.logs import get_logger, logging

# Size in bytes
# TODO: move me into the configuration
MAX_ZIP_SIZE = 2147483648  # 2 gb
####################

log = get_logger(__name__)
'''
These are the paths of the locations on the
local filesystem inside the celery worker
containers where the data is copied to / expected
to reside.

Note: The bind-mount from the host is defined
in workers.yml, so if you change the /usr/local
here, you need to change it there too.
'''
mount_point = seadata_vars.get('resources_mountpoint')  # '/usr/share'
if mount_point is None:
    log.exit("Unable to obtain variable: SEADATA_RESOURCES_MOUNTPOINT")
middle_path_ingestion = seadata_vars.get('workspace_ingestion')  # 'ingestion'
middle_path_orders = seadata_vars.get('workspace_orders')  # 'orders'
mybatchpath = os.path.join(mount_point, middle_path_ingestion)
myorderspath = os.path.join(mount_point, middle_path_orders)

ext_api = ImportManagerAPI()
celery_app = CeleryExt.celery_app

#####################
# https://stackoverflow.com/q/16040039
log.debug('celery: disable prefetching')
# disable prefetching
celery_app.conf.update(
    # CELERYD_PREFETCH_MULTIPLIER=1,
    # CELERY_ACKS_LATE=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

#####################
# worker connection to redis
if gethostname() != 'rapydo_server':
    redis_vars = detector.load_group(label='redis')
    from redis import StrictRedis
    pid_prefix = redis_vars.get('prefix')
    r = StrictRedis(redis_vars.get('host'))

####################
# preparing b2handle stuff
pmaker = PIDgenerator()
logging.getLogger('b2handle').setLevel(logging.WARNING)
b2handle_client = b2handle.instantiate_for_read_access()


def notify_error(error, payload, backdoor, task, extra=None, subject=None):

    error_message = "Error %s: %s" % (error[0], error[1])
    log.error(error_message)
    if extra:
        log.error(str(extra))

    payload['errors'] = []
    e = {
        "error": error[0],
        "description": error[1],
    }
    if subject is not None:
        e['subject'] = subject

    payload['errors'].append(e)

    if backdoor:
        log.warning(
            "The following json should be sent to ImportManagerAPI, " +
            "but you enabled the backdoor")
        log.info(payload)
    else:
        ext_api.post(payload)

    task_errors = [error_message]
    if extra:
        task_errors.append(str(extra))
    task.update_state(state="FAILED", meta={
        'errors': task_errors
    })
    return 'Failed'


@celery_app.task(bind=True)
@send_errors_by_email
def download_batch(self, batch_path, local_path, myjson):

    with celery_app.app.app_context():
        log.info("I'm %s (download_batch)" % self.request.id)
        log.info("Batch irods path: %s", batch_path)
        log.info("Batch local path: %s", local_path)

        params = myjson.get('parameters', {})
        backdoor = params.pop('backdoor', False)

        batch_number = params.get("batch_number")
        if batch_number is None:
            return notify_error(
                ErrorCodes.MISSING_BATCH_NUMBER_PARAM,
                myjson, backdoor, self
            )

        download_path = params.get("download_path")
        if download_path is None:
            return notify_error(
                ErrorCodes.MISSING_DOWNLOAD_PATH_PARAM,
                myjson, backdoor, self
            )

        file_count = params.get("data_file_count")
        if file_count is None:
            return notify_error(
                ErrorCodes.MISSING_FILECOUNT_PARAM,
                myjson, backdoor, self
            )

        try:
            int(file_count)
        except BaseException:
            return notify_error(
                ErrorCodes.INVALID_FILECOUNT_PARAM,
                myjson, backdoor, self
            )

        file_name = params.get('file_name')
        if file_name is None:
            return notify_error(
                ErrorCodes.MISSING_FILENAME_PARAM,
                myjson, backdoor, self
            )

        file_size = params.get("file_size")
        if file_size is None:
            return notify_error(
                ErrorCodes.MISSING_FILESIZE_PARAM,
                myjson, backdoor, self
            )

        try:
            int(file_size)
        except BaseException:
            return notify_error(
                ErrorCodes.INVALID_FILESIZE_PARAM,
                myjson, backdoor, self
            )

        file_checksum = params.get("file_checksum")
        if file_checksum is None:
            return notify_error(
                ErrorCodes.MISSING_CHECKSUM_PARAM,
                myjson, backdoor, self
            )

        imain = celery_app.get_service(service='irods')
        if not imain.is_collection(batch_path):
            return notify_error(
                ErrorCodes.BATCH_NOT_FOUND,
                myjson, backdoor, self
            )

        # 1 - download the file
        download_url = os.path.join(download_path, file_name)
        log.info("Downloading file from %s", download_url)
        try:
            r = requests.get(download_url, stream=True, verify=False)
        except requests.exceptions.ConnectionError:
            return notify_error(
                ErrorCodes.UNREACHABLE_DOWNLOAD_PATH,
                myjson, backdoor, self,
                subject=download_url
            )

        if r.status_code != 200:

            return notify_error(
                ErrorCodes.UNREACHABLE_DOWNLOAD_PATH,
                myjson, backdoor, self,
                subject=download_url
            )

        log.info("Request status = %s", r.status_code)
        batch_file = path.join(local_path, file_name)

        with open(batch_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        # 2 - verify checksum
        log.info("Computing checksum for %s...", batch_file)
        local_file_checksum = hashlib.md5(
            open(batch_file, 'rb').read()
        ).hexdigest()

        if local_file_checksum.lower() != file_checksum.lower():
            return notify_error(
                ErrorCodes.CHECKSUM_DOESNT_MATCH,
                myjson, backdoor, self,
                subject=file_name
            )
        log.info("File checksum verified for %s", batch_file)

        # 3 - verify size
        local_file_size = os.path.getsize(batch_file)
        if local_file_size != int(file_size):
            log.error(
                "File size %s for %s, expected %s",
                local_file_size, batch_file, file_size
            )
            return notify_error(
                ErrorCodes.FILESIZE_DOESNT_MATCH,
                myjson, backdoor, self,
                subject=file_name
            )

        log.info("File size verified for %s", batch_file)

        # 4 - decompress
        d = os.path.splitext(os.path.basename(batch_file))[0]
        local_unzipdir = path.join(local_path, d)

        if os.path.isdir(local_unzipdir):
            log.warning("%s already exist, removing it", local_unzipdir)
            rmtree(local_unzipdir, ignore_errors=True)

        path.create(local_unzipdir, directory=True, force=True)
        log.info("Local unzip dir = %s", local_unzipdir)

        log.info("Unzipping %s", batch_file)
        zip_ref = None
        try:
            zip_ref = zipfile.ZipFile(batch_file, 'r')
        except FileNotFoundError:
            return notify_error(
                ErrorCodes.UNZIP_ERROR_FILE_NOT_FOUND,
                myjson, backdoor, self,
                subject=file_name
            )

        except zipfile.BadZipFile:
            return notify_error(
                ErrorCodes.UNZIP_ERROR_INVALID_FILE,
                myjson, backdoor, self,
                subject=file_name
            )

        if zip_ref is not None:
            zip_ref.extractall(local_unzipdir)
            zip_ref.close()

        # 6 - verify num files?
        local_file_count = 0
        for f in os.listdir(local_unzipdir):
            local_file_count += 1
        log.info("Unzipped %d files from %s", local_file_count, batch_file)

        if local_file_count != int(file_count):
            log.error("Expected %s files for %s", file_count, batch_file)
            return notify_error(
                ErrorCodes.UNZIP_ERROR_WRONG_FILECOUNT,
                myjson, backdoor, self,
                subject=file_name
            )

        log.info("File count verified for %s", batch_file)

        rmtree(local_unzipdir, ignore_errors=True)

        # 7 - copy file from B2HOST filesystem to irods

        '''
        The data is copied from the path on the
        local filesystem inside the celery worker
        container (/usr/share/batches/<batch_id>),
        which is a directory mounted from the host,
        to the irods_path (usually /myzone/batches/<batch_id>)
        '''

        irods_batch_file = os.path.join(batch_path, file_name)
        log.debug("Copying %s into %s...", batch_file, irods_batch_file)

        imain.put(batch_file, irods_batch_file)

        # NOTE: permissions are inherited thanks to the ACL already SET
        # Not needed to set ownership to username
        log.info("Copied: %s", irods_batch_file)

        request_edmo_code = myjson.get('edmo_code')
        ext_api.post(myjson, backdoor=backdoor, edmo_code=request_edmo_code)
        return "COMPLETED"


@celery_app.task(bind=True)
@send_errors_by_email
def move_to_production_task(self, batch_id, irods_path, myjson):

    with celery_app.app.app_context():

        self.update_state(
            state="STARTING", meta={'total': None, 'step': 0, 'errors': 0})

        ###############
        log.info("I'm %s (move_to_production_task)!" % self.request.id)
        local_path = path.join(mybatchpath, batch_id, return_str=True)
        # log.warning("Vars:\n%s\n%s\n%s", local_path, irods_path, myjson)
        # icom = celery_app.get_service(service='irods', user='httpapi')
        imain = celery_app.get_service(service='irods')

        ###############
        # from glob import glob
        # # files = glob(path.join(local_path, '*', return_str=True))
        # all_files = path.join(local_path, '**', '*', return_str=True)
        # files = glob(all_files, recursive=True)
        # log.info(files)

        ###############
        out_data = []
        errors = []
        counter = 0
        param_key = 'parameters'
        params = myjson.get(param_key, {})
        elements = params.get('pids', {})
        backdoor = params.pop('backdoor', False)
        total = len(elements)
        self.update_state(state="PROGRESS", meta={
            'total': total, 'step': counter, 'errors': len(errors)})

        if elements is None:
            return notify_error(
                ErrorCodes.MISSING_PIDS_LIST,
                myjson, backdoor, self
            )

        for element in elements:

            temp_id = element.get('temp_id')  # do not pop
            record_id = element.get('format_n_code')
            current_file_name = path.last_part(temp_id)
            local_element = path.join(local_path, temp_id, return_str=False)

            # log.info('Element: %s', element)
            # if local_element in files:
            if path.file_exists_and_nonzero(local_element):
                log.info('Found: %s', local_element)
            else:
                log.error('NOT found: %s', local_element)
                errors.append({
                    "error": ErrorCodes.INGESTION_FILE_NOT_FOUND[0],
                    "description": ErrorCodes.INGESTION_FILE_NOT_FOUND[1],
                    "subject": record_id,
                })

                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter, 'errors': len(errors)})
                continue

            ###############
            # 1. copy file (irods)
            ifile = path.join(irods_path, current_file_name, return_str=True)
            try:
                imain.put(str(local_element), ifile)
            except BaseException as e:
                log.error(e)
                errors.append({
                    "error": ErrorCodes.UNABLE_TO_MOVE_IN_PRODUCTION[0],
                    "description": ErrorCodes.UNABLE_TO_MOVE_IN_PRODUCTION[1],
                    "subject": record_id,
                })

                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter, 'errors': len(errors)})
                continue
            log.debug("Moved: %s" % current_file_name)

            ###############
            # 2. request pid (irule)
            try:
                PID = pmaker.pid_request(imain, ifile)
            except BaseException as e:
                log.error(e)
                errors.append({
                    "error": ErrorCodes.UNABLE_TO_ASSIGN_PID[0],
                    "description": ErrorCodes.UNABLE_TO_ASSIGN_PID[1],
                    "subject": record_id,
                })

                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter, 'errors': len(errors)})
                continue
            log.info('PID: %s', PID)
            # # save inside the cache? (both)
            r.set(PID, ifile)
            r.set(ifile, PID)

            ###############
            # 3. set metadata (icat)
            metadata, _ = imain.get_metadata(ifile)
            # log.pp(metadata)
            for key in md.keys:
                if key not in metadata:
                    value = element.get(key, '***MISSING***')
                    args = {'path': ifile, key: value}
                    imain.set_metadata(**args)

            ###############
            # 4. remove the batch file?
            # or move it into a "completed/" folder
            # where we can check if it was already done?
            pass

            ###############
            # 5. add to logs
            element['pid'] = PID
            out_data.append(element)

            counter += 1
            self.update_state(state="PROGRESS", meta={
                'total': total, 'step': counter, 'errors': len(errors)}
            )

        ###############
        # Notify the CDI API
        myjson[param_key]['pids'] = out_data
        msg = prepare_message(self, isjson=True)
        for key, value in msg.items():
            myjson[key] = value
        if len(errors) > 0:
            myjson['errors'] = errors
        ext_api.post(myjson, backdoor=backdoor)

        out = {
            'total': total, 'step': counter,
            'errors': len(errors), 'out': out_data
        }
        self.update_state(state="COMPLETED", meta=out)
        return out

    return myjson


@celery_app.task(bind=True)
@send_errors_by_email
def unrestricted_order(self, order_id, order_path, zip_file_name, myjson):

    with celery_app.app.app_context():

        log.info("I'm %s (unrestricted_order)" % self.request.id)

        params = myjson.get('parameters', {})
        backdoor = params.pop('backdoor', False)
        pids = params.get('pids', [])
        total = len(pids)
        self.update_state(
            state="STARTING",
            meta={'total': total, 'step': 0, 'errors': 0, 'verified': 0})

        ##################
        # SETUP
        # local_dir = path.build([TMPDIR, order_id])
        local_dir = path.join(myorderspath, order_id)
        path.create(local_dir, directory=True, force=True)
        local_zip_dir = path.join(local_dir, 'tobezipped')
        path.create(local_zip_dir, directory=True, force=True)

        imain = celery_app.get_service(service='irods')
        # log.pp(order_path)

        ##################
        # Verify pids
        files = {}
        errors = []
        counter = 0
        verified = 0
        for pid in pids:

            ################
            # avoid empty pids?
            if '/' not in pid or len(pid) < 10:
                continue

            ################
            # Check the cache first
            ifile = r.get(pid)
            if ifile is not None:
                files[pid] = ifile.decode()
                verified += 1
                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter, 'verified': verified,
                    'errors': len(errors)}
                )
                continue

            # otherwise b2handle remotely
            try:
                b2handle_output = b2handle_client.retrieve_handle_record(pid)
            except BaseException as e:
                self.update_state(state="FAILED", meta={
                    'total': total, 'step': counter,
                    'verified': verified,
                    'errors': len(errors)}
                )
                return notify_error(
                    ErrorCodes.B2HANDLE_ERROR,
                    myjson, backdoor, self
                )
            log.verbose('Handle called')
            # TODO: you should cache the obtained PID?

            ################
            if b2handle_output is None:
                errors.append({
                    "error": ErrorCodes.PID_NOT_FOUND[0],
                    "description": ErrorCodes.PID_NOT_FOUND[1],
                    "subject": pid
                })
                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter, 'errors': len(errors)})

                log.warning("PID not found: %s", pid)
            else:
                ipath = pmaker.parse_pid_dataobject_path(b2handle_output)
                log.verbose("PID verified: %s\n(%s)", pid, ipath)
                files[pid] = ipath

                verified += 1
                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter, 'verified': verified,
                    'errors': len(errors)}
                )
        log.debug("PID files: %s", len(files))

        # Recover files
        for pid, ipath in files.items():

            # Copy files from irods into a local TMPDIR
            filename = path.last_part(ipath)
            local_file = path.build([local_zip_dir, filename])

            #########################
            #########################
            # FIXME: can this have better performances?
            #########################
            if not path.file_exists_and_nonzero(local_file):
                try:
                    with open(local_file, 'wb') as target:
                        with imain.get_dataobject(ipath).open('r+') as source:
                            for line in source:
                                target.write(line)
                except BaseException as e:
                    errors.append({
                        "error": ErrorCodes.UNABLE_TO_DOWNLOAD_FILE[0],
                        "description": ErrorCodes.UNABLE_TO_DOWNLOAD_FILE[1],
                        "subject": filename
                    })
                    self.update_state(state="PROGRESS", meta={
                        'total': total, 'step': counter,
                        'errors': len(errors)})
                    continue

                # log.debug("Copy to local: %s", local_file)
            #########################
            #########################

            counter += 1
            if counter % 1000 == 0:
                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter,
                    'verified': verified,
                    'errors': len(errors)}
                )
                log.info("%s pids already processed", counter)
            # # Set current file to the metadata collection
            # if pid not in metadata:
            #     md = {pid: ipath}
            #     imain.set_metadata(order_path, **md)
            #     log.verbose("Set metadata")

        zip_ipath = None
        if counter > 0:
            ##################
            # Zip the dir
            zip_local_file = path.join(local_dir, zip_file_name)
            log.debug("Zip local path: %s", zip_local_file)
            if not path.file_exists_and_nonzero(zip_local_file):
                path.compress(local_zip_dir, str(zip_local_file))
                log.info("Compressed in: %s", zip_local_file)

            ##################
            # Copy the zip into irods
            zip_ipath = path.join(order_path, zip_file_name, return_str=True)
            imain.put(str(zip_local_file), zip_ipath)  # NOTE: always overwrite
            log.info("Copied zip to irods: %s", zip_ipath)

            if os.path.getsize(zip_local_file) > MAX_ZIP_SIZE:
                log.warning("Zip too large, splitting %s", zip_local_file)

                # Create a sub folder for split files. If already exists,
                # remove it before to start from a clean environment
                split_path = path.join(local_dir, "unrestricted_zip_split")
                # split_path is an object
                rmtree(str(split_path), ignore_errors=True)
                # path create requires a path object
                path.create(split_path, directory=True, force=True)
                # path object is no longer required, cast to string
                split_path = str(split_path)

                # Execute the split of the whole zip
                bash = BashCommands()
                split_params = [
                    '-n', MAX_ZIP_SIZE,
                    '-b', split_path,
                    zip_local_file
                ]
                try:
                    out = bash.execute_command(
                        '/usr/bin/zipsplit', split_params)
                except ProcessExecutionError as e:

                    if 'Entry is larger than max split size' in e.stdout:
                        reg = 'Entry too big to split, read, or write \((.*)\)'
                        extra = None
                        m = re.search(reg, e.stdout)
                        if m:
                            extra = m.group(1)
                        return notify_error(
                            ErrorCodes.ZIP_SPLIT_ENTRY_TOO_LARGE,
                            myjson, backdoor, self, extra=extra
                        )
                    else:
                        log.error(e.stdout)

                    return notify_error(
                        ErrorCodes.ZIP_SPLIT_ERROR,
                        myjson, backdoor, self, extra=str(zip_local_file)
                    )

                # Parsing the zipsplit output to determine the output name
                # Long names are truncated to 7 characters, we want to come
                # back to the previous names
                out_array = out.split('\n')
                # example of out_array[1]:
                # creating: /usr/share/orders/zip_split/130900/order_p1.zip
                regexp = 'creating: %s/(.*)1.zip' % split_path
                m = re.search(regexp, out_array[1])
                if not m:
                    return notify_error(
                        ErrorCodes.ZIP_SPLIT_ERROR,
                        myjson, backdoor, self, extra=str(zip_local_file)
                    )

                # Remove the .zip extention
                base_filename, _ = os.path.splitext(zip_file_name)
                prefix = m.group(1)
                for index in range(1, 100):
                    subzip_file = path.append_compress_extension(
                        "%s%d" % (prefix, index)
                    )
                    subzip_path = path.join(split_path, subzip_file)

                    if not path.file_exists_and_nonzero(subzip_path):
                        log.warning(
                            "%s not found, break the loop", subzip_path)
                        break

                    subzip_ifile = path.append_compress_extension(
                        "%s%d" % (base_filename, index)
                    )
                    subzip_ipath = path.join(order_path, subzip_ifile)

                    subzip_file = path.append_compress_extension(
                        "%s%d" % (prefix, index)
                    )
                    log.info("Uploading %s -> %s", subzip_path, subzip_ipath)
                    imain.put(str(subzip_path), str(subzip_ipath))

        #########################
        # NOTE: should I close the iRODS session ?
        #########################
        pass
        # imain.prc

        ##################
        # CDI notification
        reqkey = 'request_id'
        msg = prepare_message(self, isjson=True)
        zipcount = 0
        if counter > 0:
            # FIXME: what about when restricted is there?
            zipcount += 1
        myjson['parameters'] = {
            # "request_id": msg['request_id'],
            reqkey: myjson[reqkey],
            "order_number": order_id,
            "zipfile_name": params['file_name'],
            "file_count": counter,
            "zipfile_count": zipcount,
        }
        for key, value in msg.items():
            if key == reqkey:
                continue
            myjson[key] = value
        if len(errors) > 0:
            myjson['errors'] = errors
        myjson[reqkey] = self.request.id
        # log.pp(myjson)
        ext_api.post(myjson, backdoor=backdoor)

        ##################
        out = {
            'total': total, 'step': counter,
            'verified': verified, 'errors': len(errors),
            'zip': zip_ipath,
        }
        self.update_state(state="COMPLETED", meta=out)
        return out

    return myjson


@celery_app.task(bind=True)
@send_errors_by_email
def download_restricted_order(self, order_id, order_path, myjson):

    with celery_app.app.app_context():

        myjson['parameters']['request_id'] = myjson['request_id']
        myjson['request_id'] = self.request.id

        params = myjson.get('parameters', {})

        backdoor = params.pop('backdoor', False)

        # Make sure you have a path with no trailing slash
        order_path = order_path.rstrip('/')

        imain = celery_app.get_service(service='irods')
        if not imain.is_collection(order_path):
            return notify_error(
                ErrorCodes.ORDER_NOT_FOUND,
                myjson, backdoor, self
            )

        order_number = params.get("order_number")
        if order_number is None:
            return notify_error(
                ErrorCodes.MISSING_ORDER_NUMBER_PARAM,
                myjson, backdoor, self
            )

        # check if order_numer == order_id ?

        download_path = params.get("download_path")
        if download_path is None:
            return notify_error(
                ErrorCodes.MISSING_DOWNLOAD_PATH_PARAM,
                myjson, backdoor, self
            )

        # NAME OF FINAL ZIP
        filename = params.get('zipfile_name')
        if filename is None:
            return notify_error(
                ErrorCodes.MISSING_ZIPFILENAME_PARAM,
                myjson, backdoor, self
            )

        base_filename = filename
        if filename.endswith('.zip'):
            log.warning('%s already contains extention .zip', filename)
            # TO DO: save base_filename as filename - .zip
        else:
            filename = path.append_compress_extension(filename)

        final_zip = order_path + '/' + filename.rstrip('/')

        log.info("order_id = %s", order_id)
        log.info("order_path = %s", order_path)
        log.info("final_zip = %s", final_zip)

        # ############################################

        # INPUT PARAMETERS CHECKS

        # zip file uploaded from partner
        file_name = params.get('file_name')
        if file_name is None:
            return notify_error(
                ErrorCodes.MISSING_FILENAME_PARAM,
                myjson, backdoor, self
            )

        file_size = params.get("file_size")
        if file_size is None:
            return notify_error(
                ErrorCodes.MISSING_FILESIZE_PARAM,
                myjson, backdoor, self
            )
        try:
            int(file_size)
        except BaseException:
            return notify_error(
                ErrorCodes.INVALID_FILESIZE_PARAM,
                myjson, backdoor, self
            )

        file_count = params.get("data_file_count")
        if file_count is None:
            return notify_error(
                ErrorCodes.MISSING_FILECOUNT_PARAM,
                myjson, backdoor, self
            )
        try:
            int(file_count)
        except BaseException:
            return notify_error(
                ErrorCodes.INVALID_FILECOUNT_PARAM,
                myjson, backdoor, self
            )

        file_checksum = params.get("file_checksum")
        if file_checksum is None:
            return notify_error(
                ErrorCodes.MISSING_CHECKSUM_PARAM,
                myjson, backdoor, self
            )

        self.update_state(state="PROGRESS")

        errors = []
        local_finalzip_path = None
        log.info("Merging zip file", file_name)

        if not file_name.endswith('.zip'):
            file_name = path.append_compress_extension(file_name)

        # 1 - download in local-dir
        download_url = os.path.join(download_path, file_name)
        log.info("Downloading file from %s", download_url)
        try:
            r = requests.get(download_url, stream=True, verify=False)
        except requests.exceptions.ConnectionError:
            return notify_error(
                ErrorCodes.UNREACHABLE_DOWNLOAD_PATH,
                myjson, backdoor, self,
                subject=download_url
            )

        if r.status_code != 200:

            return notify_error(
                ErrorCodes.UNREACHABLE_DOWNLOAD_PATH,
                myjson, backdoor, self,
                subject=download_url
            )

        log.info("Request status = %s", r.status_code)

        local_dir = path.join(myorderspath, order_id)
        path.create(local_dir, directory=True, force=True)
        log.info("Local dir = %s", local_dir)

        local_zip_path = path.join(local_dir, file_name)
        log.info("partial_zip = %s", local_zip_path)

        with open(local_zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        # 2 - verify checksum
        log.info("Computing checksum for %s...", local_zip_path)
        local_file_checksum = hashlib.md5(
            open(local_zip_path, 'rb').read()
        ).hexdigest()

        if local_file_checksum.lower() != file_checksum.lower():
            return notify_error(
                ErrorCodes.CHECKSUM_DOESNT_MATCH,
                myjson, backdoor, self,
                subject=file_name
            )
        log.info("File checksum verified for %s", local_zip_path)

        # 3 - verify size
        local_file_size = os.path.getsize(local_zip_path)
        if local_file_size != int(file_size):
            log.error(
                "File size %s for %s, expected %s",
                local_file_size, local_zip_path, file_size
            )
            return notify_error(
                ErrorCodes.FILESIZE_DOESNT_MATCH,
                myjson, backdoor, self,
                subject=file_name
            )

        log.info("File size verified for %s", local_zip_path)

        # 4 - decompress
        d = os.path.splitext(os.path.basename(local_zip_path))[0]
        local_unzipdir = path.join(local_dir, d)

        if os.path.isdir(local_unzipdir):
            log.warning("%s already exist, removing it", local_unzipdir)
            rmtree(local_unzipdir, ignore_errors=True)

        path.create(local_dir, directory=True, force=True)
        log.info("Local unzip dir = %s", local_unzipdir)

        log.info("Unzipping %s", local_zip_path)
        zip_ref = None
        try:
            zip_ref = zipfile.ZipFile(local_zip_path, 'r')
        except FileNotFoundError:
            return notify_error(
                ErrorCodes.UNZIP_ERROR_FILE_NOT_FOUND,
                myjson, backdoor, self,
                subject=file_name
            )

        except zipfile.BadZipFile:
            return notify_error(
                ErrorCodes.UNZIP_ERROR_INVALID_FILE,
                myjson, backdoor, self,
                subject=file_name
            )

        if zip_ref is not None:
            zip_ref.extractall(local_unzipdir)
            zip_ref.close()

        # 5 - verify num files?
        local_file_count = 0
        for f in os.listdir(local_unzipdir):
            local_file_count += 1
        log.info("Unzipped %d files from %s", local_file_count, local_zip_path)

        if local_file_count != int(file_count):
            log.error("Expected %s files for %s", file_count, local_zip_path)
            return notify_error(
                ErrorCodes.UNZIP_ERROR_WRONG_FILECOUNT,
                myjson, backdoor, self,
                subject=file_name
            )

        log.info("File count verified for %s", local_zip_path)

        log.info("Verifying final zip: %s", final_zip)
        # 6 - check if final_zip exists
        if not imain.exists(final_zip):
            # 7 - if not, simply copy partial_zip -> final_zip
            log.info("Final zip does not exist, copying partial zip")
            try:
                imain.put(local_zip_path, final_zip)
            except IrodsException as e:
                log.error(str(e))
                return notify_error(
                    ErrorCodes.B2SAFE_UPLOAD_ERROR,
                    myjson, backdoor, self,
                    subject=file_name
                )
            local_finalzip_path = local_zip_path
        else:
            # 8 - if already exists merge zips
            log.info("Already exists, merge zip files")

            log.info("Copying zipfile locally")
            local_finalzip_path = path.join(
                local_dir, os.path.basename(final_zip))
            imain.open(final_zip, local_finalzip_path)

            log.info("Reading local zipfile")
            zip_ref = None
            try:
                zip_ref = zipfile.ZipFile(local_finalzip_path, 'a')
            except FileNotFoundError:
                log.error("Local file not found: %s", local_finalzip_path)
                return notify_error(
                    ErrorCodes.UNZIP_ERROR_FILE_NOT_FOUND,
                    myjson, backdoor, self,
                    subject=final_zip
                )

            except zipfile.BadZipFile:
                log.error("Invalid local file: %s", local_finalzip_path)
                return notify_error(
                    ErrorCodes.UNZIP_ERROR_INVALID_FILE,
                    myjson, backdoor, self,
                    subject=final_zip
                )

            log.info("Adding files to local zipfile")
            if zip_ref is not None:
                try:
                    for f in os.listdir(local_unzipdir):
                        # log.debug("Adding %s", f)
                        zip_ref.write(
                            os.path.join(local_unzipdir, f), f)
                    zip_ref.close()
                except BaseException:
                    return notify_error(
                        ErrorCodes.UNABLE_TO_CREATE_ZIP_FILE,
                        myjson, backdoor, self,
                        subject=final_zip
                    )

            log.info("Creating a backup copy of final zip")
            backup_zip = final_zip + ".bak"
            if imain.is_dataobject(backup_zip):
                log.info("%s already exists, removing previous backup")
                imain.remove(backup_zip)
            imain.move(final_zip, backup_zip)

            log.info("Uploading final updated zip")
            imain.put(local_finalzip_path, final_zip)

            # imain.remove(local_zip_path)
        rmtree(local_unzipdir, ignore_errors=True)

        self.update_state(state="COMPLETED")

        if local_finalzip_path is None:
            log.warning("local_finalzip_path is None, unable to check size of file zip")
        elif os.path.getsize(local_finalzip_path) > MAX_ZIP_SIZE:
            log.warning("Zip too large, splitting %s", local_finalzip_path)

            # Create a sub folder for split files. If already exists,
            # remove it before to start from a clean environment
            split_path = path.join(local_dir, "restricted_zip_split")
            # split_path is an object
            rmtree(str(split_path), ignore_errors=True)
            # path create requires a path object
            path.create(split_path, directory=True, force=True)
            # path object is no longer required, cast to string
            split_path = str(split_path)

            # Execute the split of the whole zip
            bash = BashCommands()
            split_params = [
                '-n', MAX_ZIP_SIZE,
                '-b', split_path,
                local_finalzip_path
            ]
            try:
                out = bash.execute_command(
                    '/usr/bin/zipsplit', split_params)
            except ProcessExecutionError as e:

                if 'Entry is larger than max split size' in e.stdout:
                    reg = 'Entry too big to split, read, or write \((.*)\)'
                    extra = None
                    m = re.search(reg, e.stdout)
                    if m:
                        extra = m.group(1)
                    return notify_error(
                        ErrorCodes.ZIP_SPLIT_ENTRY_TOO_LARGE,
                        myjson, backdoor, self, extra=extra
                    )
                else:
                    log.error(e.stdout)

                return notify_error(
                    ErrorCodes.ZIP_SPLIT_ERROR,
                    myjson, backdoor, self, extra=str(local_finalzip_path)
                )
            # Parsing the zipsplit output to determine the output name
            # Long names are truncated to 7 characters, we want to come
            # back to the previous names
            out_array = out.split('\n')
            # example of out_array[1]:
            # creating: /usr/share/orders/zip_split/130900/order_p1.zip
            regexp = 'creating: %s/(.*)1.zip' % split_path
            m = re.search(regexp, out_array[1])
            if not m:
                return notify_error(
                    ErrorCodes.INVALID_ZIP_SPLIT_OUTPUT,
                    myjson, backdoor, self, extra=str(local_finalzip_path)
                )

            prefix = m.group(1)
            for index in range(1, 100):
                subzip_file = path.append_compress_extension(
                    "%s%d" % (prefix, index)
                )
                subzip_path = path.join(split_path, subzip_file)

                if not path.file_exists_and_nonzero(subzip_path):
                    log.warning("%s not found, break the loop", subzip_path)
                    break

                subzip_ifile = path.append_compress_extension(
                    "%s%d" % (base_filename, index)
                )
                subzip_ipath = path.join(order_path, subzip_ifile)

                subzip_file = path.append_compress_extension(
                    "%s%d" % (prefix, index)
                )
                log.info("Uploading %s -> %s", subzip_path, subzip_ipath)
                imain.put(str(subzip_path), str(subzip_ipath))

        if len(errors) > 0:
            myjson['errors'] = errors
        ext_api.post(myjson, backdoor=backdoor)
        return "COMPLETED"

        # 0 - avoid concurrent execution, introduce a cache like:
        # http://loose-bits.com/2010/10/distributed-task-locking-in-celery.html
        # https://pypi.org/project/celery_once/


@celery_app.task(bind=True)
@send_errors_by_email
def delete_orders(self, orders_path, local_orders_path, myjson):

    with celery_app.app.app_context():

        if 'parameters' not in myjson:
            myjson['parameters'] = {}
            # TODO Raise error already here!
            # Or even before reaching asynchronous job...

        myjson['parameters']['request_id'] = myjson['request_id']
        myjson['request_id'] = self.request.id
        # TODO Why? We end up with two different request_ids,
        # one from the client, one from our system.

        params = myjson.get('parameters', {})

        backdoor = params.pop('backdoor', False)

        orders = myjson['parameters'].pop('orders', None)
        if orders is None:
            return notify_error(
                ErrorCodes.MISSING_ORDERS_PARAMETER,
                myjson, backdoor, self
            )
        total = len(orders)

        if total == 0:
            return notify_error(
                ErrorCodes.EMPTY_ORDERS_PARAMETER,
                myjson, backdoor, self
            )

        imain = celery_app.get_service(service='irods')

        errors = []
        counter = 0
        for order in orders:

            counter += 1
            self.update_state(state="PROGRESS", meta={
                'total': total, 'step': counter, 'errors': len(errors)})

            order_path = path.join(orders_path, order)
            local_order_path = path.join(local_orders_path, order)
            log.info("Delete request for order collection: %s", order_path)
            log.info("Delete request for order path: %s", local_order_path)

            if not imain.is_collection(order_path):
                errors.append({
                    "error": ErrorCodes.ORDER_NOT_FOUND[0],
                    "description": ErrorCodes.ORDER_NOT_FOUND[1],
                    "subject": order,
                })

                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter, 'errors': len(errors)})
                continue

            ##################
            # TODO: remove the iticket?
            pass

            # TODO: I should also revoke the task?

            imain.remove(order_path, recursive=True)

            if os.path.isdir(local_order_path):
                rmtree(local_order_path, ignore_errors=True)

        if len(errors) > 0:
            myjson['errors'] = errors
        ext_api.post(myjson, backdoor=backdoor)
        return "COMPLETED"


@celery_app.task(bind=True)
@send_errors_by_email
def delete_batches(self, batches_path, local_batches_path, myjson):

    with celery_app.app.app_context():

        if 'parameters' not in myjson:
            myjson['parameters'] = {}

        myjson['parameters']['request_id'] = myjson['request_id']
        myjson['request_id'] = self.request.id

        params = myjson.get('parameters', {})

        backdoor = params.pop('backdoor', False)

        batches = myjson['parameters'].pop('batches', None)
        if batches is None:
            return notify_error(
                ErrorCodes.MISSING_BATCHES_PARAMETER,
                myjson, backdoor, self
            )
        total = len(batches)

        if total == 0:
            return notify_error(
                ErrorCodes.EMPTY_BATCHES_PARAMETER,
                myjson, backdoor, self
            )

        imain = celery_app.get_service(service='irods')

        errors = []
        counter = 0
        for batch in batches:

            counter += 1
            self.update_state(state="PROGRESS", meta={
                'total': total, 'step': counter, 'errors': len(errors)})

            batch_path = path.join(batches_path, batch)
            local_batch_path = path.join(local_batches_path, batch)
            log.info("Delete request for batch collection %s", batch_path)
            log.info("Delete request for batch path %s", local_batch_path)

            if not imain.is_collection(batch_path):
                errors.append({
                    "error": ErrorCodes.BATCH_NOT_FOUND[0],
                    "description": ErrorCodes.BATCH_NOT_FOUND[1],
                    "subject": batch,
                })

                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter, 'errors': len(errors)})
                continue
            imain.remove(batch_path, recursive=True)

            if os.path.isdir(local_batch_path):
                rmtree(local_batch_path, ignore_errors=True)

        if len(errors) > 0:
            myjson['errors'] = errors
        ext_api.post(myjson, backdoor=backdoor)
        return "COMPLETED"


@celery_app.task(bind=True)
@send_errors_by_email
def cache_batch_pids(self, irods_path):

    with celery_app.app.app_context():

        log.info("Task cache_batch_pids working on: %s", irods_path)
        imain = celery_app.get_service(service='irods')

        stats = {
            'total': 0,
            'skipped': 0,
            'cached': 0,
            'errors': 0,
        }

        for current in imain.list(irods_path):
            ifile = path.join(irods_path, current, return_str=True)
            stats['total'] += 1

            pid = r.get(ifile)
            if pid is not None:
                stats['skipped'] += 1
                log.debug(
                    '%d: file %s already cached with PID: %s',
                    stats['total'], ifile, pid
                )
                self.update_state(state="PROGRESS", meta=stats)
                continue

            metadata, _ = imain.get_metadata(ifile)
            pid = metadata.get('PID')
            if pid is None:
                stats['errors'] += 1
                log.warning(
                    '%d: file %s has not a PID assigned',
                    stats['total'], ifile, pid
                )
                self.update_state(state="PROGRESS", meta=stats)
                continue

            r.set(pid, ifile)
            r.set(ifile, pid)
            log.very_verbose(
                '%d: file %s cached with PID %s',
                stats['total'], ifile, pid
            )
            stats['cached'] += 1
            self.update_state(state="PROGRESS", meta=stats)

        self.update_state(state="COMPLETED", meta=stats)
        log.info(stats)
        return stats


@celery_app.task(bind=True)
@send_errors_by_email
def inspect_pids_cache(self):

    with celery_app.app.app_context():

        log.info("Inspecting cache...")
        counter = 0
        cache = {}
        # for key in r.scan_iter("%s*" % pid_prefix):
        for key in r.scan_iter("*"):
            folder = os.path.dirname(r.get(key))

            prefix = str(key).split("/")[0]
            if prefix not in cache:
                cache[prefix] = {}

            if folder not in cache[prefix]:
                cache[prefix][folder] = 1
            else:
                cache[prefix][folder] += 1

            counter += 1
            if counter % 10000 == 0:
                log.info("%d pids inspected...", counter)

        for prefix in cache:
            for pid_path in cache[prefix]:
                log.info(
                    "%d pids with prefix %s from path: %s",
                    cache[prefix][pid_path], prefix, pid_path
                )


@celery_app.task(bind=True)
@send_errors_by_email
def list_resources(self, batch_path, order_path, myjson):

    with celery_app.app.app_context():

        imain = celery_app.get_service(service='irods')

        param_key = 'parameters'

        if param_key not in myjson:
            myjson[param_key] = {}

        myjson[param_key]['request_id'] = myjson['request_id']
        myjson['request_id'] = self.request.id

        params = myjson.get(param_key, {})
        backdoor = params.pop('backdoor', False)

        if param_key not in myjson:
            myjson[param_key] = {}

        myjson[param_key]['batches'] = []
        batches = imain.list(batch_path)
        for n in batches:
            myjson[param_key]['batches'].append(n)

        myjson[param_key]['orders'] = []
        orders = imain.list(order_path)
        for n in orders:
            myjson[param_key]['orders'].append(n)

        ext_api.post(myjson, backdoor=backdoor)

        return "COMPLETED"
