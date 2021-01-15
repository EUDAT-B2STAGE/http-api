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

        c = celery.get_instance()
        task = c.celery_app.send_task("inspect_pids_cache")
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

            c = celery.get_instance()
            task = c.celery_app.send_task("cache_batch_pids", args=[collection])
            log.info("Async job: {}", task.id)

            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors("B2SAFE is temporarily unavailable", code=503)
