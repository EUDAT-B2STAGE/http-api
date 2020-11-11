"""
Ingestion process submission to upload the SeaDataNet marine data.
"""
import requests
from b2stage.endpoints.commons import path
from b2stage.endpoints.commons.endpoint import (
    BATCH_MISCONFIGURATION,
    ENABLED_BATCH,
    MISSING_BATCH,
    NOT_FILLED_BATCH,
    PARTIALLY_ENABLED_BATCH,
    EudatEndpoint,
)
from irods.exception import NetworkException
from restapi import decorators
from restapi.connectors import celery
from restapi.services.uploader import Uploader
from restapi.utilities.logs import log
from seadata.endpoints.commons.cluster import (
    INGESTION_DIR,
    MOUNTPOINT,
    ClusterContainerEndpoint,
)
from seadata.endpoints.commons.queue import log_into_queue, prepare_message
from seadata.endpoints.commons.seadatacloud import EndpointsInputSchema

ingestion_user = "RM"
BACKDOOR_SECRET = "howdeepistherabbithole"


class IngestionEndpoint(Uploader, EudatEndpoint, ClusterContainerEndpoint):
    """ Create batch folder and upload zip files inside it """

    labels = ["ingestion"]

    @decorators.auth.require()
    @decorators.endpoint(
        path="/ingestion/<batch_id>",
        summary="Check if the ingestion batch is enabled",
        responses={
            200: "Batch enabled",
            400: "Batch misconfiguration",
            404: "Batch not enabled or lack of permissions",
        },
    )
    def get(self, batch_id):

        log.info("Batch request: {}", batch_id)
        # json = {'batch_id': batch_id}
        # msg = prepare_message(
        #     self, json=json, user=ingestion_user, log_string='start')
        # log_into_queue(self, msg)

        ########################
        # get irods session

        try:
            imain = self.get_main_irods_connection()

            batch_path = self.get_irods_batch_path(imain, batch_id)
            local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
            log.info("Batch irods path: {}", batch_path)
            log.info("Batch local path: {}", local_path)

            batch_status, batch_files = self.get_batch_status(
                imain, batch_path, local_path
            )

            ########################
            # if not imain.is_collection(batch_path):
            if batch_status == MISSING_BATCH:
                return self.send_errors(
                    f"Batch '{batch_id}' not enabled or you have no permissions",
                    code=404,
                )

            if batch_status == BATCH_MISCONFIGURATION:
                log.error(
                    "Misconfiguration: {} files in {} (expected 1)",
                    len(batch_files),
                    batch_path,
                )
                return self.send_errors(
                    f"Misconfiguration for batch_id {batch_id}",
                    # Bad Resource
                    code=410,
                )

            data = {}
            data["batch"] = batch_id
            if batch_status == NOT_FILLED_BATCH:
                data["status"] = "not_filled"
            elif batch_status == ENABLED_BATCH:
                data["status"] = "enabled"
            elif batch_status == PARTIALLY_ENABLED_BATCH:
                data["status"] = "partially_enabled"

            data["files"] = batch_files
            return self.response(data)
        except requests.exceptions.ReadTimeout:
            return self.send_errors("B2SAFE is temporarily unavailable", code=503)
        except NetworkException as e:
            log.error(e)
            return self.send_errors("Could not connect to B2SAFE host", code=503)

    @decorators.auth.require()
    @decorators.use_kwargs(EndpointsInputSchema)
    @decorators.endpoint(
        path="/ingestion/<batch_id>",
        summary="Request to import a zip file to the ingestion cloud",
        responses={
            200: "Request unqueued for download",
            404: "Batch not enabled or lack of permissions",
        },
    )
    def post(self, batch_id, **json_input):

        obj = self.init_endpoint()
        try:
            imain = self.get_main_irods_connection()

            batch_path = self.get_irods_batch_path(imain, batch_id)
            log.info("Batch irods path: {}", batch_path)
            local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
            log.info("Batch local path: {}", local_path)

            """
            Create the batch folder if not exists
            """

            # Log start (of enable) into RabbitMQ
            log_msg = prepare_message(
                self,
                json={"batch_id": batch_id},
                user=ingestion_user,
                log_string="start",
            )
            log_into_queue(self, log_msg)

            ##################
            # Does it already exist?
            # Create the collection and set permissions in irods
            if not imain.is_collection(batch_path):

                imain.create_collection_inheritable(batch_path, obj.username)
            else:
                log.warning("Irods batch collection {} already exists", batch_path)

            # Create the folder on filesystem
            if not path.file_exists_and_nonzero(local_path):

                # Create superdirectory and directory on file system:
                try:
                    # TODO: REMOVE THIS WHEN path.create() has parents=True!
                    import os

                    superdir = os.path.join(MOUNTPOINT, INGESTION_DIR)
                    if not os.path.exists(superdir):
                        log.debug("Creating {}...", superdir)
                        os.mkdir(superdir)
                        log.info("Created {}...", superdir)
                    path.create(local_path, directory=True, force=True)
                except (FileNotFoundError, PermissionError) as e:
                    err_msg = 'Could not create directory "{}" ({})'.format(
                        local_path, e
                    )
                    log.critical(err_msg)
                    log.info("Removing collection from irods ({})", batch_path)
                    imain.remove(batch_path, recursive=True, force=True)
                    return self.send_errors(err_msg, code=500)

            else:
                log.debug("Batch path already exists on filesytem")

            # Log end (of enable) into RabbitMQ
            log_msg = prepare_message(
                self, status="enabled", user=ingestion_user, log_string="end"
            )
            log_into_queue(self, log_msg)

            # Download the file into the batch folder

            celery_app = celery.get_instance()
            task = celery_app.download_batch.apply_async(
                args=[batch_path, str(local_path), json_input],
                queue="ingestion",
                routing_key="ingestion",
            )
            log.info("Async job: {}", task.id)
            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors("B2SAFE is temporarily unavailable", code=503)

    @decorators.auth.require()
    @decorators.use_kwargs(EndpointsInputSchema)
    @decorators.endpoint(
        path="/ingestion",
        summary="Delete one or more ingestion batches",
        responses={200: "Async job submitted for ingestion batches removal"},
    )
    def delete(self, **json_input):

        try:
            imain = self.get_main_irods_connection()
            batch_path = self.get_irods_batch_path(imain)
            local_batch_path = str(path.join(MOUNTPOINT, INGESTION_DIR))
            log.debug("Batch collection: {}", batch_path)
            log.debug("Batch path: {}", local_batch_path)

            celery_app = celery.get_instance()
            task = celery_app.delete_batches.apply_async(
                args=[batch_path, local_batch_path, json_input],
                queue="ingestion",
                routing_key="ingestion",
            )
            log.info("Async job: {}", task.id)
            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors("B2SAFE is temporarily unavailable", code=503)
