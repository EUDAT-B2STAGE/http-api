import requests
from b2stage.endpoints.commons.endpoint import EudatEndpoint
from restapi import decorators
from restapi.connectors import celery
from restapi.utilities.logs import log
from seadata.endpoints.commons.cluster import ClusterContainerEndpoint
from seadata.endpoints.commons.seadatacloud import EndpointsInputSchema


class ListResources(EudatEndpoint, ClusterContainerEndpoint):

    labels = ["helper"]

    @decorators.auth.require()
    @decorators.use_kwargs(EndpointsInputSchema)
    @decorators.endpoint(
        path="/resourceslist",
        summary="Request a list of existing batches and orders",
        responses={200: "Returning id of async request"},
    )
    def post(self, **json_input):

        try:
            imain = self.get_main_irods_connection()
            celery_app = celery.get_instance()
            task = celery_app.list_resources.apply_async(
                args=[
                    self.get_irods_batch_path(imain),
                    self.get_irods_order_path(imain),
                    json_input,
                ]
            )
            log.info("Async job: {}", task.id)
            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors("B2SAFE is temporarily unavailable", code=503)
