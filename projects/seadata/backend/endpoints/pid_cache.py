import os

import requests
from b2stage.endpoints.commons.b2access import B2accessUtilities
from restapi import decorators
from restapi.connectors import celery
from restapi.exceptions import RestApiException
from restapi.services.authentication import Role
from restapi.utilities.logs import log
from seadata.endpoints.commons.cluster import ClusterContainerEndpoint


class PidCache(ClusterContainerEndpoint, B2accessUtilities):

    labels = ["helper"]

    @decorators.auth.require_any(Role.ADMIN, Role.STAFF)
    @decorators.endpoint(
        path="/pidcache",
        summary="Retrieve values from the pid cache",
        responses={200: "Async job started"},
    )
    def get(self):

        celery_app = celery.get_instance()
        task = celery_app.inspect_pids_cache.apply_async()
        log.info("Async job: {}", task.id)
        return self.return_async_id(task.id)

    @decorators.auth.require_any(Role.ADMIN, Role.STAFF)
    @decorators.endpoint(
        path="/pidcache/<batch_id>",
        summary="Fill the pid cache",
        responses={200: "Async job started"},
    )
    def post(self, batch_id):

        try:
            imain = self.get_main_irods_connection()
            ipath = self.get_irods_production_path(imain)

            collection = os.path.join(ipath, batch_id)
            if not imain.exists(collection):
                raise RestApiException(f"Invalid batch id {batch_id}", status_code=404)

            celery_app = celery.get_instance()
            task = celery_app.cache_batch_pids.apply_async(args=[collection])
            log.info("Async job: {}", task.id)

            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors("B2SAFE is temporarily unavailable", code=503)
