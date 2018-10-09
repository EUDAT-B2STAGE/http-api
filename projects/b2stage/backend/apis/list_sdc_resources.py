# -*- coding: utf-8 -*-

from b2stage.apis.commons.cluster import ClusterContainerEndpoint as Endpoint
from utilities.logs import get_logger
from restapi.flask_ext.flask_celery import CeleryExt

log = get_logger(__name__)


class ListResources(Endpoint):

    def get(self):

        json_input = self.get_input()
        task = CeleryExt.list_resources.apply_async(
            args=[self.get_batch_path(), self.get_order_path(), json_input]
        )
        log.warning("Async job: %s", task.id)
        return self.return_async_id(task.id)
