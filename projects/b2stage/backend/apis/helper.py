# -*- coding: utf-8 -*-

from restapi.rest.definition import EndpointResource
# from restapi.services.detect import detector
from utilities.logs import get_logger
from restapi.flask_ext.flask_celery import CeleryExt

log = get_logger(__name__)


class Helper(EndpointResource):

    def get(self, batch_id):

        log.info("Received a test HTTP request")

        # log.error('Service %s unavailable', service_name)
        # return self.send_errors(
        #     message='Server internal error. Please contact adminers.',
        #     # code=hcodes.HTTP_BAD_NOTFOUND
        # )

        prefix_batches = 'import01june_rabbithole_500000_'
        imain = self.get_service_instance(service_name='irods')
        ipath = self.get_batch_path(imain)
        collections = imain.list(ipath)

        for collection in collections:
            if collection.startswith(prefix_batches):
                task = CeleryExt.cache_batch_pids.apply_async(
                    args=[collection], countdown=1)
                log.warning("Async job: %s", task.id)
                break

        response = 'Hello world!'
        return self.force_response(response)
