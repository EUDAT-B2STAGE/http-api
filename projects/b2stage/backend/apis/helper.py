# -*- coding: utf-8 -*-


import os
import time
# from restapi.rest.definition import EndpointResource
from b2stage.apis.commons.cluster import ClusterContainerEndpoint as Endpoint
# from restapi.services.detect import detector
from utilities.logs import get_logger
from restapi.flask_ext.flask_celery import CeleryExt

log = get_logger(__name__)


class Helper(Endpoint):

    def get(self, batch_id):

        prefix_batches = 'import01june_rabbithole_500000_'
        imain = self.get_service_instance(service_name='irods')
        ipath = self.get_production_path(imain)
        collections = imain.list(ipath)

        tasks = {}
        for collection in collections:
            current = os.path.join(ipath, collection)
            if collection.startswith(prefix_batches):
                task = CeleryExt.cache_batch_pids.apply_async(args=[current])
                log.info("Async job: %s", task.id)
                tasks[collection] = task.id
                break

        return tasks

    def post(self):

        task = CeleryExt.pids_cached_to_json.apply_async()
        log.warning("Async job: %s", task.id)
        return {'async': task.id}
