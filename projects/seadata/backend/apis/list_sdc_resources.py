# -*- coding: utf-8 -*-

from b2stage.apis.commons.endpoint import EudatEndpoint
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from utilities.logs import get_logger
from restapi.flask_ext.flask_celery import CeleryExt

log = get_logger(__name__)


class ListResources(EudatEndpoint, ClusterContainerEndpoint):

    def post(self):

        # imain = self.get_service_instance(service_name='irods')
        imain = self.get_main_irods_connection()
        json_input = self.get_input()
        task = CeleryExt.list_resources.apply_async(
            args=[
                self.get_irods_batch_path(imain),
                self.get_irods_order_path(imain),
                json_input
            ]
        )
        log.info("Async job: %s", task.id)
        return self.return_async_id(task.id)
