# -*- coding: utf-8 -*-

import os
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from restapi import decorators as decorate
from restapi.exceptions import RestApiException
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger
from restapi.flask_ext.flask_celery import CeleryExt

log = get_logger(__name__)


class PidCache(ClusterContainerEndpoint):

    @decorate.catch_error()
    def get(self):

        task = CeleryExt.inspect_pids_cache.apply_async()
        log.warning("Async job: %s", task.id)
        return self.return_async_id(task.id)

    @decorate.catch_error()
    def post(self, batch_id):

        # imain = self.get_service_instance(service_name='irods')
        imain = self.get_main_irods_connection()
        ipath = self.get_irods_production_path(imain)

        collection = os.path.join(ipath, batch_id)
        if not imain.exists(collection):
            raise RestApiException(
                "Invalid batch id %s" % batch_id,
                status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        task = CeleryExt.cache_batch_pids.apply_async(args=[collection])
        log.info("Async job: %s", task.id)

        return self.return_async_id(task.id)
