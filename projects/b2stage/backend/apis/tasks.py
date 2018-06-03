# -*- coding: utf-8 -*-

"""
Tasks for background operations.

DEPRECATED: This is just a template
"""

from restapi.rest.definition import EndpointResource
from utilities.logs import get_logger

log = get_logger(__name__)


#################
# REST CLASS
class Tasks(EndpointResource):

    # def get(self):
    #     return "To do"

    def post(self):

        log.info("Request to submit a celery task")
        from restapi.flask_ext.flask_celery import CeleryExt
        task = CeleryExt.test_task.apply_async(
            args=[200000], countdown=1
        )
        return task.id
