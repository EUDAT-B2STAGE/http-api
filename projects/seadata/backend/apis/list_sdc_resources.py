# -*- coding: utf-8 -*-

import requests

from b2stage.apis.commons.endpoint import EudatEndpoint
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from restapi import decorators
from restapi.connectors.celery import CeleryExt
from restapi.utilities.logs import log
from restapi.utilities.htmlcodes import hcodes


class ListResources(EudatEndpoint, ClusterContainerEndpoint):

    labels = ['helper']
    POST = {
        '/resourceslist': {
            'custom': {},
            'summary': 'Request a list of existing batches and orders',
            'responses': {'200': {'description': 'returning id of async request'}},
        }
    }

    @decorators.auth.required()
    def post(self):

        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            json_input = self.get_input()
            task = CeleryExt.list_resources.apply_async(
                args=[
                    self.get_irods_batch_path(imain),
                    self.get_irods_order_path(imain),
                    json_input,
                ]
            )
            log.info("Async job: {}", task.id)
            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=hcodes.HTTP_SERVICE_UNAVAILABLE
            )
