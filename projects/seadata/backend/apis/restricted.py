import requests
from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi import decorators
from restapi.services.uploader import Uploader
from restapi.utilities.logs import log
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from seadata.apis.commons.seadatacloud import EndpointsInputSchema


class Restricted(Uploader, EudatEndpoint, ClusterContainerEndpoint):

    labels = ["restricted"]
    _POST = {
        "/restricted/<order_id>": {
            "summary": "Request to import a zip file into a restricted order",
            "responses": {"200": {"description": "Request unqueued for download"}},
        }
    }

    # Request for a file download into a restricted order
    @decorators.auth.require_any("admin_root", "staff_user")
    @decorators.use_kwargs(EndpointsInputSchema, locations=["json", "form", "query"])
    def post(self, order_id, **json_input):

        try:
            imain = self.get_main_irods_connection()
            order_path = self.get_irods_order_path(imain, order_id)
            if not imain.is_collection(order_path):
                obj = self.init_endpoint()
                # Create the path and set permissions
                imain.create_collection_inheritable(order_path, obj.username)

            celery = self.get_service_instance("celery")
            task = celery.download_restricted_order.apply_async(
                args=[order_id, order_path, json_input],
                queue="restricted",
                routing_key="restricted",
            )
            log.info("Async job: {}", task.id)
            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors("B2SAFE is temporarily unavailable", code=503)
