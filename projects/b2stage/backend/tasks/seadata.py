# -*- coding: utf-8 -*-

from restapi.flask_ext.flask_celery import CeleryExt
from utilities.logs import get_logger

log = get_logger(__name__)
# celery_app = current_app.extensions.get('celery').celery_app
celery_app = CeleryExt.celery_app


@celery_app.task(bind=True)
def move_to_production_task(self, batch_id, irods_path, filenames):

    path = '/usr/share/batches'

    with celery_app.app.app_context():

        log.info("I'm %s" % self.request.id)
        log.warning("Vars:\n%s\n%s\n%s", batch_id, irods_path, filenames)
        from glob import glob as listfiles
        files = listfiles('%s/%s' % (path, batch_id))
        log.info(files)
        return files
