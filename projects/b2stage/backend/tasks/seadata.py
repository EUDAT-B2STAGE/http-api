# -*- coding: utf-8 -*-

from socket import gethostname
from utilities import path
from restapi.flask_ext.flask_celery import CeleryExt
from b2stage.apis.commons.queue import prepare_message
from b2stage.apis.commons.seadatacloud import \
    Metadata as md, ImportManagerAPI, ErrorCodes
from b2stage.apis.commons.b2handle import PIDgenerator, b2handle
from restapi.services.detect import detector

from utilities.logs import get_logger, logging


####################
mybatchpath = '/usr/share/batches'
myorderspath = '/usr/share/orders'

ext_api = ImportManagerAPI()
log = get_logger(__name__)
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


####################
def notify_server_problems(myjson):
    myjson['errors'] = {
        "error": ErrorCodes.INTERNAL_SERVER_ERROR,
        "description": "Internal error, restart your request",
        # "subject": pid
    }
    ext_api.post(myjson)


####################
@celery_app.task(bind=True)
def send_to_workers_task(self, batch_id, irods_path, zip_name, backdoor):

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
                from shutil import unpack_archive
                unpack_archive(str(local_element), str(local_path), 'zip')

    return str(local_element)


@celery_app.task(bind=True)
def move_to_production_task(self, batch_id, irods_path, myjson):

    with celery_app.app.app_context():

        self.update_state(
            state="STARTING", meta={'total': None, 'step': 0, 'errors': 0})

        ###############
        log.info("I'm %s" % self.request.id)
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
        notified = False
        param_key = 'parameters'
        elements = myjson.get(param_key, {}).get('pids', {})
        total = len(elements)
        testing_mode = myjson.get('test_mode', 'empty') == 'initial_load'
        self.update_state(state="PROGRESS", meta={
            'total': total, 'step': counter, 'errors': len(errors)})

        for element in elements:

            tmp = element.get('temp_id')  # do not pop
            current = path.last_part(tmp)
            local_element = path.join(local_path, tmp, return_str=False)

            # log.info('Element: %s', element)
            # if local_element in files:
            if path.file_exists_and_nonzero(local_element):
                log.info('Found: %s', local_element)
            else:
                log.error('NOT found: %s', local_element)
                errors.append({
                    "error": ErrorCodes.INGESTION_FILE_NOT_FOUND,
                    "description": "File requested not found",
                    "subject": tmp,
                })

                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter, 'errors': len(errors)})
                continue

            ###############
            # 1. copy file (irods)
            ifile = path.join(irods_path, current, return_str=True)
            try:
                imain.put(str(local_element), ifile)
            except BaseException as e:
                log.error(e)
                notified = True
                notify_server_problems(myjson)
                break
            else:
                log.debug("Moved: %s" % current)

            ###############
            # 2. request pid (irule)
            try:
                PID = pmaker.pid_request(imain, ifile)
            except BaseException as e:
                notified = True
                notify_server_problems(myjson)
                break
            else:
                log.info('PID: %s', PID)
                # # save inside the cache? (both)
                # r.set(PID, ifile)
                # r.set(ifile, PID)

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
        if not notified:
            if testing_mode:
                log.verbose('skipping CDI API')
            else:
                myjson[param_key]['pids'] = out_data
                msg = prepare_message(self, isjson=True)
                for key, value in msg.items():
                    myjson[key] = value
                if len(errors) > 0:
                    myjson['errors'] = errors
                ext_api.post(myjson)

        self.update_state(
            state="COMPLETED", meta={
                'total': total, 'step': counter, 'errors': len(errors)}
        )

    return myjson


@celery_app.task(bind=True)
def unrestricted_order(self, order_id, order_path, zip_file_name, myjson):

    with celery_app.app.app_context():

        log.info("I'm %s" % self.request.id)
        failed = False

        ##################
        main_key = 'parameters'
        params = myjson.get(main_key, {})
        key = 'pids'
        pids = params.get(key, [])
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
        log.pp(order_path)
        # metadata, _ = imain.get_metadata(order_path)
        # log.pp(metadata)

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

            # TODO: should I try the cache first?
            # NOTE: only with a backdoor initially?
            pass

            # otherwise b2handle remotely
            try:
                b2handle_output = b2handle_client.retrieve_handle_record(pid)
            except BaseException as e:
                failed = True
                notify_server_problems(myjson)
                break
            else:
                log.verbose('Handle called')

            ################
            if b2handle_output is None:
                errors.append({
                    "error": ErrorCodes.PID_NOT_FOUND,
                    "description": "PID not found",
                    "subject": pid
                })
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

        if failed:
            self.update_state(state="FAILED", meta={
                'total': total, 'step': counter,
                'verified': verified,
                'errors': len(errors)}
            )
            return 'Failed'
        else:
            log.debug("PID files: %s", files)

        ##################
        # Recover files
        for pid, ipath in files.items():
            # print(pid, ipath)

            # Copy files from irods into a local TMPDIR
            filename = path.last_part(ipath)
            local_file = path.build([local_zip_dir, filename])

            # Copy if not there yet
            if not path.file_exists_and_nonzero(local_file):
                try:
                    # TODO: check if I already have a wrapper for this
                    with open(local_file, 'wb') as target:
                        with imain.get_dataobject(ipath).open('r+') as source:
                            for line in source:
                                target.write(line)
                except BaseException as e:
                    failed = True
                    notify_server_problems(myjson)
                    break
                else:
                    log.debug("Copy to local: %s", local_file)

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

        if failed:
            self.update_state(state="FAILED", meta={
                'total': total, 'step': counter, 'errors': len(errors)}
            )
            return 'Failed'

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

        ##################
        # CDI notification
        # FIXME: add a backdoor for EUDAT tests
        if True:
            reqkey = 'request_id'
            msg = prepare_message(self, isjson=True)
            zipcount = 0
            if counter > 0:
                # FIXME: what about when restricted is there?
                zipcount += 1
            myjson[main_key] = {
                # "request_id": msg['request_id'],
                reqkey: myjson[reqkey],
                "order": order_id,
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
            ext_api.post(myjson)

        ##################
        self.update_state(
            state="COMPLETED",
            meta={
                'total': total, 'step': counter, 'verified': verified,
                'errors': len(errors)})

    return myjson


@celery_app.task(bind=True)
def cache_batch_pids(self, irods_path):

    with celery_app.app.app_context():

        log.info("I'm %s" % self.request.id)
        log.warning("Working off: %s", irods_path)
        imain = celery_app.get_service(service='irods')

        for current in imain.list(irods_path):
            ifile = path.join(irods_path, current, return_str=True)
            # log.verbose('Current: %s', ifile)
            pid = r.get(ifile)
            if pid is not None:
                log.debug('PID: %s', pid)
            else:
                metadata, _ = imain.get_metadata(ifile)
                pid = metadata.get('PID')
                if pid is None:
                    log.warning("Cannot find pid for: %s", ifile)
                else:
                    r.set(pid, ifile)
                    r.set(ifile, pid)
                    log.very_verbose("Set cache: %s", current)
                    break


@celery_app.task(bind=True)
def pids_cached_to_json(self):

    with celery_app.app.app_context():

        for key in r.scan_iter("%s*" % pid_prefix):
            log.info("Key: %s = %s", key, r.get(key))
            # break
