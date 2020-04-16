# -*- coding: utf-8 -*-

"""
Ingestion process submission to upload the SeaDataNet marine data.
"""

import requests

from b2stage.apis.commons.endpoint import EudatEndpoint
from b2stage.apis.commons.endpoint import MISSING_BATCH, NOT_FILLED_BATCH
from b2stage.apis.commons.endpoint import PARTIALLY_ENABLED_BATCH, ENABLED_BATCH
from b2stage.apis.commons.endpoint import BATCH_MISCONFIGURATION
from restapi import decorators
from restapi.services.uploader import Uploader
from restapi.connectors.celery import CeleryExt
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from seadata.apis.commons.cluster import INGESTION_DIR, MOUNTPOINT
from seadata.apis.commons.queue import log_into_queue, prepare_message
from restapi.utilities.htmlcodes import hcodes
from b2stage.apis.commons import path
from restapi.utilities.logs import log
from irods.exception import NetworkException

ingestion_user = 'RM'
BACKDOOR_SECRET = 'howdeepistherabbithole'


class IngestionEndpoint(Uploader, EudatEndpoint, ClusterContainerEndpoint):
    """ Create batch folder and upload zip files inside it """

    labels = ['ingestion']
    GET = {
        '/ingestion/<string:batch_id>': {
            'custom': {},
            'summary': 'Check if the ingestion batch is enabled',
            'responses': {
                '404': {'description': 'Batch not enabled or lack of permissions'},
                '400': {'description': 'Batch misconfiguration'},
                '200': {'description': 'Batch enabled'},
            },
        }
    }
    POST = {
        '/ingestion/<string:batch_id>': {
            'custom': {},
            'summary': 'Request to import a zip file to the ingestion cloud',
            'responses': {
                '200': {'description': 'Request unqueued for download'},
                '404': {'description': 'Batch not enabled or lack of permissions'},
            },
        }
    }
    DELETE = {
        '/ingestion': {
            'custom': {},
            'summary': 'Delete one or more ingestion batches',
            'responses': {
                '200': {
                    'description': 'Async job submitted for ingestion batches removal'
                }
            },
        }
    }

    @decorators.auth.required()
    def get(self, batch_id):

        log.info("Batch request: {}", batch_id)
        # json = {'batch_id': batch_id}
        # msg = prepare_message(
        #     self, json=json, user=ingestion_user, log_string='start')
        # log_into_queue(self, msg)

        ########################
        # get irods session

        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()

            batch_path = self.get_irods_batch_path(imain, batch_id)
            local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
            log.info("Batch irods path: {}", batch_path)
            log.info("Batch local path: {}", local_path)

            batch_status, batch_files = self.get_batch_status(imain, batch_path, local_path)

            ########################
            # if not imain.is_collection(batch_path):
            if batch_status == MISSING_BATCH:
                return self.send_errors(
                    "Batch '{}' not enabled or you have no permissions".format(batch_id),
                    code=hcodes.HTTP_BAD_NOTFOUND,
                )

            if batch_status == BATCH_MISCONFIGURATION:
                log.error(
                    'Misconfiguration: {} files in {} (expected 1)',
                    len(batch_files),
                    batch_path,
                )
                return self.send_errors(
                    "Misconfiguration for batch_id {}".format(batch_id),
                    code=hcodes.HTTP_BAD_RESOURCE,
                )

            data = {}
            data['batch'] = batch_id
            if batch_status == NOT_FILLED_BATCH:
                data['status'] = 'not_filled'
            elif batch_status == ENABLED_BATCH:
                data['status'] = 'enabled'
            elif batch_status == PARTIALLY_ENABLED_BATCH:
                data['status'] = 'partially_enabled'

            data['files'] = batch_files
            return self.response(data)
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=hcodes.HTTP_SERVICE_UNAVAILABLE
            )
        except NetworkException as e:
            log.error(e)
            return self.send_errors(
                "Could not connect to B2SAFE host",
                code=hcodes.HTTP_SERVICE_UNAVAILABLE
            )

    @decorators.auth.required()
    def post(self, batch_id):
        json_input = self.get_input()

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
                self, json={'batch_id': batch_id}, user=ingestion_user, log_string='start'
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
                        log.debug('Creating {}...', superdir)
                        os.mkdir(superdir)
                        log.info('Created {}...', superdir)
                    path.create(local_path, directory=True, force=True)
                except (FileNotFoundError, PermissionError) as e:
                    err_msg = 'Could not create directory "{}" ({})'.format(
                        local_path, e)
                    log.critical(err_msg)
                    log.info('Removing collection from irods ({})', batch_path)
                    imain.remove(batch_path, recursive=True, force=True)
                    return self.send_errors(err_msg, code=hcodes.HTTP_SERVER_ERROR)

            else:
                log.debug("Batch path already exists on filesytem")

            # Log end (of enable) into RabbitMQ
            log_msg = prepare_message(
                self, status='enabled', user=ingestion_user, log_string='end'
            )
            log_into_queue(self, log_msg)

            """
                Download the file into the batch folder
            """

            task = CeleryExt.download_batch.apply_async(
                args=[batch_path, str(local_path), json_input],
                queue='ingestion',
                routing_key='ingestion',
            )
            log.info("Async job: {}", task.id)
            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=hcodes.HTTP_SERVICE_UNAVAILABLE
            )

    @decorators.auth.required()
    def delete(self):

        json_input = self.get_input()

        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            batch_path = self.get_irods_batch_path(imain)
            local_batch_path = str(path.join(MOUNTPOINT, INGESTION_DIR))
            log.debug("Batch collection: {}", batch_path)
            log.debug("Batch path: {}", local_batch_path)

            task = CeleryExt.delete_batches.apply_async(
                args=[batch_path, local_batch_path, json_input],
                queue='ingestion',
                routing_key='ingestion',
            )
            log.info("Async job: {}", task.id)
            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=hcodes.HTTP_SERVICE_UNAVAILABLE
            )
