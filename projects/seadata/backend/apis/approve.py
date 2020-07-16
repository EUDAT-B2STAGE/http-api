"""
Move data from ingestion to production
"""
import requests
from b2stage.apis.commons.b2handle import B2HandleEndpoint
from restapi import decorators
from restapi.utilities.logs import log
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from seadata.apis.commons.seadatacloud import EndpointsInputSchema
from seadata.apis.commons.seadatacloud import Metadata as md


#################
# REST CLASS
class MoveToProductionEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):

    labels = ["ingestion"]
    _POST = {
        "/ingestion/<batch_id>/approve": {
            "summary": "Approve files in a batch that are passing all QCs",
            "responses": {"200": {"description": "Registration executed"}},
        }
    }

    @decorators.auth.require()
    @decorators.use_kwargs(EndpointsInputSchema, locations=["json", "form", "query"])
    def post(self, batch_id, **json_input):

        params = json_input.get("parameters", {})
        if len(params) < 1:
            return self.send_errors("parameters is empty", code=400)

        files = params.get("pids", {})
        if len(files) < 1:
            return self.send_errors("pids' parameter is empty list", code=400)

        filenames = []
        for data in files:

            if not isinstance(data, dict):
                return self.send_errors(
                    "File list contains at least one wrong entry", code=400,
                )

            # print("TEST", data)
            for key in md.keys:  # + [md.tid]:
                value = data.get(key)
                if value is None:
                    error = f"Missing parameter: {key}"
                    return self.send_errors(error, code=400)

                error = None
                value_len = len(value)
                if value_len > md.max_size:
                    error = f"Param '{key}': exceeds size {md.max_size}"
                elif value_len < 1:
                    error = f"Param '{key}': empty"
                if error is not None:
                    return self.send_errors(error, code=400)

            filenames.append(data.get(md.tid))

        ################
        # 1. check if irods path exists
        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            batch_path = self.get_irods_batch_path(imain, batch_id)
            log.debug("Batch path: {}", batch_path)

            if not imain.is_collection(batch_path):
                return self.send_errors(
                    f"Batch '{batch_id}' not enabled (or no permissions)", code=404,
                )

            ################
            # 2. make batch_id directory in production if not existing
            prod_path = self.get_irods_production_path(imain, batch_id)
            log.debug("Production path: {}", prod_path)
            obj = self.init_endpoint()
            imain.create_collection_inheritable(prod_path, obj.username)

            ################
            # ASYNC
            log.info("Submit async celery task")

            celery = self.get_service_instance("celery")
            task = celery.move_to_production_task.apply_async(
                args=[batch_id, batch_path, prod_path, json_input],
                queue="ingestion",
                routing_key="ingestion",
            )
            log.info("Async job: {}", task.id)

            return self.return_async_id(task.id)

        except requests.exceptions.ReadTimeout:
            return self.send_errors("B2SAFE is temporarily unavailable", code=503)
