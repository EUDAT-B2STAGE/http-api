# -*- coding: utf-8 -*-

from restapi.flask_ext.flask_celery import CeleryExt
from utilities.logs import get_logger

log = get_logger(__name__)
# celery_app = current_app.extensions.get('celery').celery_app
celery_app = CeleryExt.celery_app


@celery_app.task(bind=True)
def move_to_production_task(self, batch_id, irods_path, myjson):

    path = '/usr/share/batch'

    with celery_app.app.app_context():

        ###############
        log.info("I'm %s" % self.request.id)
        local_path = '%s/%s' % (path, batch_id)
        log.warning("Vars:\n%s\n%s\n%s", local_path, irods_path, myjson)

        ###############
        from glob import glob
        files = glob('%s/*' % local_path)
        log.info(files)

        ###############
        for element in myjson.get('parameters', {}).get('pids', {}):
            current = element.get('temp_id')
            log.info('Element: %s', element)
            if current in files:
                log.info('%s: found', current)
            else:
                log.error('%s: NOT found', current)

        ###############
        return files
