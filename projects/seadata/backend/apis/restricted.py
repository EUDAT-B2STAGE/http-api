# -*- coding: utf-8 -*-

import requests
from b2stage.apis.commons.endpoint import EudatEndpoint
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from restapi.services.uploader import Uploader
from restapi.protocols.bearer import authentication
from restapi.flask_ext.flask_celery import CeleryExt
from utilities.logs import get_logger

log = get_logger(__name__)


class Restricted(Uploader, EudatEndpoint, ClusterContainerEndpoint):

    # schema_expose = True
    labels = ['seadatacloud', 'restricted']
    depends_on = ['SEADATA_PROJECT']
    POST = {
        '/restricted/<string:order_id>': {
            'custom': {},
            'summary': 'Request to import a zip file into a restricted order',
            'responses': {'200': {'description': 'Request unqueued for download'}},
        }
    }

    # Request for a file download into a restricted order
    @authentication.required(roles=['admin_root', 'staff_user'], required_roles='any')
    def post(self, order_id):

        json_input = self.get_input()

        try:
            imain = self.get_main_irods_connection()
            order_path = self.get_irods_order_path(imain, order_id)
            if not imain.is_collection(order_path):
                obj = self.init_endpoint()
                # Create the path and set permissions
                imain.create_collection_inheritable(order_path, obj.username)

            task = CeleryExt.download_restricted_order.apply_async(
                args=[order_id, order_path, json_input]
            )
            log.info("Async job: %s", task.id)
            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "irods is temporarily unavailable",
                code=hcodes.HTTP_SERVICE_UNAVAILABLE
            )
