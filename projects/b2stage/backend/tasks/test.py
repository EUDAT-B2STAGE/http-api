# -*- coding: utf-8 -*-

from restapi.connectors.celery import CeleryExt
from restapi.utilities.logs import log

# celery_app = current_app.extensions.get('celery').celery_app
celery_app = CeleryExt.celery_app


@celery_app.task(bind=True)
def test_task(self, num):

    with celery_app.app.app_context():

        log.info("I'm {}", self.request.id)

        log.debug("Starting task to calculate {} squares!", num)
        for count in range(1, int(num)):
            x = count * count
            x = x * x
            self.update_state(state='PROGRESS',
                              meta={'current': count, 'total': num})
        log.info("Task completed, calculated up to {} squares", num)
        return "WOW, i calculated {} squares!!".format(num)
