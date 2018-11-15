# -*- coding: utf-8 -*-

import os
import hashlib
import zipfile
import json
import re
from shutil import rmtree, unpack_archive
from socket import gethostname
from plumbum.commands.processes import ProcessExecutionError
from utilities.basher import BashCommands
from utilities import path
from restapi.flask_ext.flask_celery import CeleryExt
from restapi.flask_ext.flask_irods.client import IrodsException
from b2stage.apis.commons.queue import prepare_message
from b2stage.apis.commons.seadatacloud import \
    Metadata as md, ImportManagerAPI, ErrorCodes
from b2stage.apis.commons.b2handle import PIDgenerator, b2handle
from restapi.services.detect import detector
from b2stage.apis.commons.seadatacloud import seadata_vars

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


def notify_error(error, payload, backdoor, task, extra=None):

    error_message = "Error %s: %s" % (error[0], error[1])
    log.error(error_message)
    if extra:
        log.error(str(extra))

    payload['errors'] = []
    payload['errors'].append(
        {
            "error": error[0],
            "description": error[1],
        }
    )
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
def copy_from_b2safe_to_b2host(self, batch_id, irods_path, zip_name, backdoor):
    '''
    This task copies data from irods to the B2HOST
    filesystem, so that it is available for
    pre-production qc checks.

    The data is copied from irods_path (usually
    /myzone/batches/<batch_id>) to a path on the
    local filesystem inside the celery worker
    container (/usr/share/batches/<batch_id>),
    which is a directory mounted from the host.
    '''
    local_path = path.join(mybatchpath, batch_id)
    path.create(local_path, directory=True, force=True)
    local_element = path.join(local_path, zip_name)

    with celery_app.app.app_context():

        ###############
        # pull the path from irods
        imain = celery_app.get_service(service='irods')
        log.debug("Copying %s", irods_path)
        imain.open(irods_path, local_element)
        log.info("Copied: %s", local_path)

        ###############
        # if backdoor unzip it
        if backdoor:
            log.warning('Backdoor! Unzipping: %s', local_element)
            if path.file_exists_and_nonzero(local_element):
                unpack_archive(str(local_element), str(local_path), 'zip')

    return str(local_element)


@celery_app.task(bind=True)
def copy_from_b2host_to_b2safe(self, batch_id, irods_path, zip_path, backdoor):
    '''
    This task copies data from B2HOST filesystem to irods

    The data is copied from the path on the
    local filesystem inside the celery worker
    container (/usr/share/batches/<batch_id>),
    which is a directory mounted from the host,
    to the irods_path (usually /myzone/batches/<batch_id>)
    '''
    # local_path = path.join(mybatchpath, batch_id)
    # path.create(local_path, directory=True, force=True)
    # local_element = path.join(local_path, zip_name)

    if not os.path.isfile(zip_path):
        error = "Unable to copy on B2SAFE, file not found: %s" % zip_path
        log.error(error)
        self.update_state(state="FAILED", meta={
            'errors': error
        })
        return 'Failed'

    with celery_app.app.app_context():

        imain = celery_app.get_service(service='irods')
        log.debug("Copying %s", zip_path)
        # imain.open(irods_path, local_element)
        imain.put(zip_path, irods_path)

        # NOTE: permissions are inherited thanks to the ACL already SET
        # Not needed to set ownership to username
        log.info("Copied: %s", irods_path)

    return str(irods_path)


@celery_app.task(bind=True)
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

            tmp = element.get('temp_id')  # do not pop
            current_file_name = path.last_part(tmp)
            local_element = path.join(local_path, tmp, return_str=False)

            # log.info('Element: %s', element)
            # if local_element in files:
            if path.file_exists_and_nonzero(local_element):
                log.info('Found: %s', local_element)
            else:
                log.error('NOT found: %s', local_element)
                errors.append({
                    "error": ErrorCodes.INGESTION_FILE_NOT_FOUND[0],
                    "description": ErrorCodes.INGESTION_FILE_NOT_FOUND[1],
                    "subject": tmp,
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
                    "subject": tmp,
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
                    "subject": tmp,
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

        # ###############
        # ifiles = imain.list(irods_path)
        # log.info('irods content: %s', ifiles)
        # log.verbose("\n")

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

                log.debug("Copy to local: %s", local_file)
            #########################
            #########################

            counter += 1
            self.update_state(state="PROGRESS", meta={
                'total': total, 'step': counter,
                'verified': verified,
                'errors': len(errors)}
            )
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
def create_restricted_order(self, order_id, order_path, username, myjson):

    with celery_app.app.app_context():
        log.info('Enabling restricted: order id %s', order_id)

        # Cleaning up input json
        if 'order' in myjson['parameters']:
            myjson['parameters'].pop('order', None)
        if 'order_id' in myjson['parameters']:
            myjson['parameters'].pop('order_id', None)
        myjson['parameters']['order_number'] = order_id
        myjson['parameters']['request_id'] = myjson['request_id']
        myjson['request_id'] = self.request.id

        if 'errors' not in myjson:
            myjson['errors'] = []

        params = myjson.get('parameters', {})

        backdoor = params.pop('backdoor', False)

        imain = celery_app.get_service(service='irods')
        # Make sure you have a path with no trailing slash
        order_path = order_path.rstrip('/')

        # restricted = params.get('b2access_ids')
        restricted = myjson['parameters'].pop('b2access_ids', None)
        if restricted is None:
            return notify_error(
                ErrorCodes.MISSING_PARTNERS_IDS,
                myjson, backdoor, self
            )

        ##################
        # Metadata handling
        if not imain.is_collection(order_path):
            # Create the path and set permissions
            imain.create_collection_inheritable(order_path, username)
            log.warning("Created %s because it did not exist", order_path)
            log.info("Assigned permissions to %s", username)

        valid_accounts = []
        for account in restricted:
            info = imain.get_user_info(account)
            if info is None:
                myjson["errors"].append({
                    "error": ErrorCodes.INVALID_B2ACCESS_ID[0],
                    "description": ErrorCodes.INVALID_B2ACCESS_ID[1],
                    "subject": account,
                })
                continue
            valid_accounts.append(account)


        metadata, _ = imain.get_metadata(order_path)
        # log.pp(metadata)

        # Remove if existing
        key = 'restricted'
        if key in metadata:
            imain.remove_metadata(order_path, key)
            log.info("Merge: %s and %s", metadata.get(key), valid_accounts)
            previous_restricted = json.loads(metadata.get(key))
            valid_accounts = previous_restricted + valid_accounts

        # Set restricted metadata
        string = json.dumps(valid_accounts)
        imain.set_metadata(order_path, restricted=string)
        log.debug('Flagged restricted: %s', string)

        ext_api.post(myjson, backdoor=backdoor)
        return "COMPLETED"


@celery_app.task(bind=True)
def merge_restricted_order(self, order_id, order_path, myjson):

    with celery_app.app.app_context():

        myjson['parameters']['request_id'] = myjson['request_id']
        myjson['request_id'] = self.request.id

        params = myjson.get('parameters', {})

        backdoor = params.pop('backdoor', False)

        # Make sure you have a path with no trailing slash
        order_path = order_path.rstrip('/')

        # filename = 'order_%s' % order_id
        filename = params.get('file_name')
        if filename is None:
            return notify_error(
                ErrorCodes.MISSING_FILENAME_PARAM,
                myjson, backdoor, self
            )
        base_filename = filename
        if filename.endswith('.zip'):
            log.warning('%s already contains extention .zip', filename)
            # TO DO: save base_filename as filename - .zip
        else:
            filename = path.append_compress_extension(filename)
        # final_zip = self.complete_path(order_path, filename)
        final_zip = order_path + '/' + filename.rstrip('/')

        # myjson['parameters']['zipfile_name'] = final_zip

        # zip file uploaded from partner
        zip_file = params.get('zipfile_name')
        if zip_file is None:
            return notify_error(
                ErrorCodes.MISSING_ZIPFILENAME_PARAM,
                myjson, backdoor, self
            )

        if not zip_file.endswith('.zip'):
            zip_file = path.append_compress_extension(zip_file)
        # partial_zip = self.complete_path(order_path, zip_file)
        partial_zip = order_path + '/' + zip_file.rstrip('/')

        log.info("order_id = %s", order_id)
        log.info("order_path = %s", order_path)
        log.info("partial_zip = %s", partial_zip)
        log.info("final_zip = %s", final_zip)

        file_size = params.get("file_size")
        if file_size is None:
            return notify_error(
                ErrorCodes.MISSING_FILESIZE_PARAM,
                myjson, backdoor, self
            )
        try:
            file_size = int(file_size)
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
            file_count = int(file_count)
        except BaseException:
            return notify_error(
                ErrorCodes.INVALID_FILECOUNT_PARAM,
                myjson, backdoor, self
            )

        self.update_state(state="PROGRESS")

        file_checksum = params.get("file_checksum")
        imain = celery_app.get_service(service='irods')

        # 1 - check if partial_zip exists
        if not imain.exists(partial_zip):
            return notify_error(
                ErrorCodes.FILENAME_DOESNT_EXIST,
                myjson, backdoor, self
            )

        # 2 - copy partial_zip in local-dir
        local_dir = path.join(myorderspath, order_id)
        path.create(local_dir, directory=True, force=True)
        log.info("Local dir = %s", local_dir)

        local_zip_path = path.join(
            local_dir, os.path.basename(partial_zip))
        imain.open(partial_zip, local_zip_path)

        # 3 - verify checksum
        log.info("Computing checksum...")
        local_file_checksum = hashlib.md5(
            open(local_zip_path, 'rb').read()
        ).hexdigest()

        if local_file_checksum == file_checksum:
            log.info("File checksum verified")
        else:
            return notify_error(
                ErrorCodes.CHECKSUM_DOESNT_MATCH,
                myjson, backdoor, self
            )

        # 4 - verify size
        local_file_size = os.path.getsize(local_zip_path)
        if local_file_size == file_size:
            log.info("File size verified")
        else:
            return notify_error(
                ErrorCodes.FILESIZE_DOESNT_MATCH,
                myjson, backdoor, self
            )

        # 5 - decompress
        d = os.path.splitext(os.path.basename(partial_zip))[0]
        local_unzipdir = path.join(local_dir, d)

        if os.path.isdir(local_unzipdir):
            log.warning("%s already exist, removing it", local_unzipdir)
            rmtree(local_unzipdir, ignore_errors=True)

        path.create(local_dir, directory=True, force=True)
        log.info("Local unzip dir = %s", local_unzipdir)

        log.info("Unzipping %s", partial_zip)
        zip_ref = None
        try:
            zip_ref = zipfile.ZipFile(local_zip_path, 'r')
        except FileNotFoundError:
            return notify_error(
                ErrorCodes.UNZIP_ERROR_FILE_NOT_FOUND,
                myjson, backdoor, self, extra=local_zip_path
            )
        except zipfile.BadZipFile:
            return notify_error(
                ErrorCodes.UNZIP_ERROR_INVALID_FILE,
                myjson, backdoor, self, extra=local_zip_path
            )

        if zip_ref is not None:
            zip_ref.extractall(local_unzipdir)
            zip_ref.close()

        # 6 - verify num files?
        local_file_count = 0
        for f in os.listdir(local_unzipdir):
            # log.info(f)
            local_file_count += 1
        log.info("Unzipped %d files from %s", local_file_count, partial_zip)

        if local_file_count == file_count:
            log.info("File count verified")
        else:
            return notify_error(
                ErrorCodes.UNZIP_ERROR_WRONG_FILECOUNT,
                myjson, backdoor, self
            )

        # 7 - check if final_zip exists
        if not imain.exists(final_zip):
            # 8 - if not, simply copy partial_zip -> final_zip
            log.info("Final zip does not exist, copying partial zip")
            try:
                imain.icopy(partial_zip, final_zip)
            except IrodsException as e:
                return notify_error(
                    ErrorCodes.B2SAFE_UPLOAD_ERROR,
                    myjson, backdoor, self, extra=str(e)
                )
            local_finalzip_path = local_zip_path
        else:
            # 9 - if already exists merge zips
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
                return notify_error(
                    ErrorCodes.UNZIP_ERROR_FILE_NOT_FOUND,
                    myjson, backdoor, self, extra=local_finalzip_path
                )
            except zipfile.BadZipFile:
                return notify_error(
                    ErrorCodes.UNZIP_ERROR_INVALID_FILE,
                    myjson, backdoor, self, extra=local_finalzip_path
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
                        myjson, backdoor, self, extra=local_finalzip_path
                    )

            log.info("Creating a backup copy of final zip")
            imain.move(final_zip, final_zip + ".bak")

            log.info("Uploading final updated zip")
            imain.put(local_finalzip_path, final_zip)

        self.update_state(state="COMPLETED")

        imain.remove(partial_zip)

        if os.path.getsize(local_finalzip_path) > MAX_ZIP_SIZE:
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

        ext_api.post(myjson, backdoor=backdoor)
        return "COMPLETED"

        # 0 - avoid concurrent execution, introduce a cache like:
        # http://loose-bits.com/2010/10/distributed-task-locking-in-celery.html
        # https://pypi.org/project/celery_once/


@celery_app.task(bind=True)
def delete_orders(self, orders_path, myjson):

    with celery_app.app.app_context():

        log.info("Delete request for order path %s", orders_path)

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
            log.info(order_path)

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

        if len(errors) > 0:
            myjson['errors'] = errors
        ext_api.post(myjson, backdoor=backdoor)
        return "COMPLETED"


@celery_app.task(bind=True)
def delete_batches(self, batches_path, myjson):

    with celery_app.app.app_context():

        log.info("Delete request for batch path %s", batches_path)

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

        if len(errors) > 0:
            myjson['errors'] = errors
        ext_api.post(myjson, backdoor=backdoor)
        return "COMPLETED"


@celery_app.task(bind=True)
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
def pids_cached_to_json(self):

    with celery_app.app.app_context():

        for key in r.scan_iter("%s*" % pid_prefix):
            log.info("Key: %s = %s", key, r.get(key))
            # break


@celery_app.task(bind=True)
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
