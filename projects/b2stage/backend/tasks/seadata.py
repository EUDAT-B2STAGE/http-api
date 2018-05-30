# -*- coding: utf-8 -*-

from utilities import path
from restapi.flask_ext.flask_celery import CeleryExt
from b2stage.apis.commons.queue import prepare_message
from b2stage.apis.commons.seadatacloud import \
    Metadata as md, ImportManagerAPI, ErrorCodes

from utilities.logs import get_logger

ext_api = ImportManagerAPI()
log = get_logger(__name__)
celery_app = CeleryExt.celery_app
mypath = '/usr/share/batch'


@celery_app.task(bind=True)
def send_to_workers_task(self, batch_id, irods_path, zip_name, backdoor):

    local_path = path.join(mypath, batch_id)
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
        local_path = path.join(mypath, batch_id, return_str=True)
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
        from b2stage.apis.commons.b2handle import PIDgenerator
        pmaker = PIDgenerator()

        ###############
        out_data = []
        errors = []
        param_key = 'parameters'
        elements = myjson.get(param_key, {}).get('pids', {})
        total = len(elements)
        counter = 0
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
            # 1. copy file (irods) - MAY FAIL?
            ifile = path.join(irods_path, current, return_str=True)
            imain.put(str(local_element), ifile)
            log.debug("Moved: %s" % current)

            ###############
            # 2. request pid (irule)
            # strip directory as prefix
            PID = pmaker.pid_request(imain, ifile)
            log.info('PID: %s', PID)

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
        if myjson.get('test_mode', 'empty') == 'initial_load':
            log.verbose('skipping CDI API')
        else:
            myjson[param_key]['pids'] = out_data
            msg = prepare_message(self, isjson=True)
            for key, value in msg.items():
                myjson[key] = value
            if len(errors) > 0:
                myjson['errors'] = errors
            ext_api.post(myjson)
            log.info('Notified CDI')

        self.update_state(
            state="COMPLETED", meta={
                'total': total, 'step': counter, 'errors': len(errors)}
        )
        return myjson
