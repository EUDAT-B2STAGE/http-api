# -*- coding: utf-8 -*-

import requests

from b2stage.apis.commons.endpoint import EudatEndpoint
from seadata.apis.commons.cluster import ClusterContainerEndpoint

from restapi.protocols.bearer import authentication
from restapi.flask_ext.flask_celery import CeleryExt
from restapi.utilities.logs import get_logger

log = get_logger(__name__)


class ListResources(EudatEndpoint, ClusterContainerEndpoint):

    # schema_expose = True
    labels = ['helper']
    depends_on = ['SEADATA_PROJECT']
    POST = {
        '/resourceslist': {
            'custom': {},
            'summary': 'Request a list of existing batches and orders',
            'responses': {'200': {'description': 'returning id of async request'}},
        }
    }

    @authentication.required()
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
            log.info("Async job: %s", task.id)
            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=hcodes.HTTP_SERVICE_UNAVAILABLE
            )
