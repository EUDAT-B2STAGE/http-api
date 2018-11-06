# -*- coding: utf-8 -*-

"""
This class is deprecated, use the /api/pidcache endpoint
provided by the PidCache class into pid_cache.py
"""

import os
from b2stage.apis.commons.cluster import ClusterContainerEndpoint as Endpoint
from utilities.logs import get_logger
from restapi.flask_ext.flask_celery import CeleryExt

log = get_logger(__name__)


class Helper(Endpoint):

    def get(self, batch_id):

        log.warning("This endpoint is deprecated, use POST /api/pidcache instead")

        imain = self.get_service_instance(service_name='irods')
        ipath = self.get_irods_production_path(imain)
        collections = imain.list(ipath)

        tasks = {}
        for collection in collections:
            current = os.path.join(ipath, collection)
            if collection.startswith(batch_id):
                task = CeleryExt.cache_batch_pids.apply_async(args=[current])
                log.info("Async job: %s", task.id)
                tasks[collection] = task.id
                # break

        return tasks

    def post(self):

        log.warning("This endpoint is deprecated, use GET /api/pidcache instead")

        task = CeleryExt.pids_cached_to_json.apply_async()
        log.warning("Async job: %s", task.id)
        return {'async': task.id}
