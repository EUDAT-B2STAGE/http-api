# -*- coding: utf-8 -*-

from b2stage.apis.commons.endpoint import EudatEndpoint
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from restapi.services.uploader import Uploader
from restapi.flask_ext.flask_celery import CeleryExt
from utilities.logs import get_logger

log = get_logger(__name__)


class Restricted(Uploader, EudatEndpoint, ClusterContainerEndpoint):

    # Request for a file download into a restricted order
    def post(self, order_id):

        json_input = self.get_input()

        imain = self.get_main_irods_connection()
        order_path = self.get_irods_order_path(imain, order_id)

        task = CeleryExt.download_restricted_order.apply_async(
            args=[order_id, order_path, json_input]
        )
        log.warning("Async job: %s", task.id)
        return self.return_async_id(task.id)
