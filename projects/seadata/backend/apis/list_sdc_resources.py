import requests
from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi import decorators
from restapi.utilities.logs import log
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from seadata.apis.commons.seadatacloud import EndpointsInputSchema


class ListResources(EudatEndpoint, ClusterContainerEndpoint):

    labels = ["helper"]
    _POST = {
        "/resourceslist": {
            "summary": "Request a list of existing batches and orders",
            "responses": {"200": {"description": "returning id of async request"}},
        }
    }

    @decorators.auth.require()
    @decorators.use_kwargs(EndpointsInputSchema, locations=["json", "form", "query"])
    def post(self, **json_input):

        try:
            imain = self.get_main_irods_connection()
            celery = self.get_service_instance("celery")
            task = celery.list_resources.apply_async(
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
