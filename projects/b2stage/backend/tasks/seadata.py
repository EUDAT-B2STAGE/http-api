# -*- coding: utf-8 -*-

from utilities import path
from restapi.flask_ext.flask_celery import CeleryExt
from b2stage.apis.commons.seadatacloud import Metadata as md

from utilities.logs import get_logger

log = get_logger(__name__)
# celery_app = current_app.extensions.get('celery').celery_app
celery_app = CeleryExt.celery_app


@celery_app.task(bind=True)
def move_to_production_task(self, batch_id, irods_path, myjson):

    mypath = '/usr/share/batch'

    with celery_app.app.app_context():
        ###############
        log.info("I'm %s" % self.request.id)
        local_path = path.join(mypath, batch_id, return_str=True)
        # log.warning("Vars:\n%s\n%s\n%s", local_path, irods_path, myjson)
        # icom = celery_app.get_service(service='irods', user='httpapi')
        imain = celery_app.get_service(service='irods')

        ###############
        from glob import glob
        files = glob(path.join(local_path, '*', return_str=True))
        log.info(files)
        from b2stage.apis.commons.b2handle import PIDgenerator
        pmaker = PIDgenerator()

        ###############
        for element in myjson.get('parameters', {}).get('pids', {}):
            tmp = element.pop('temp_id')
            current = path.last_part(tmp)
            local_element = path.join(local_path, tmp, return_str=True)
            # log.info('Element: %s', element)
            if local_element in files:
                log.info('Found: %s', local_element)
            else:
                log.error('NOT found: %s', local_element)
                continue
            ###############
            # 1. copy file (irods) - MAY FAIL?
            ifile = path.join(irods_path, current, return_str=True)
            imain.put(local_element, ifile)
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
        ifiles = imain.list(irods_path)
        log.info('irods content: %s', ifiles)
        log.verbose("\n")

        ###############
        return files
