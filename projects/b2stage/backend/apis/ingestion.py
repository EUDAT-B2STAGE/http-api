# -*- coding: utf-8 -*-

"""
Ingestion process submission to upload the SeaDataNet marine data.
"""

from b2stage.apis.commons.endpoint import EudatEndpoint
from b2stage.apis.commons.endpoint import MISSING_BATCH, NOT_FILLED_BATCH
from b2stage.apis.commons.endpoint import PARTIALLY_ENABLED_BATCH, ENABLED_BATCH
from b2stage.apis.commons.endpoint import BATCH_MISCONFIGURATION
from restapi.services.uploader import Uploader
from restapi.flask_ext.flask_celery import CeleryExt
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from b2stage.apis.commons.cluster import INGESTION_DIR, MOUNTPOINT
from b2stage.apis.commons.queue import log_into_queue, prepare_message
from utilities import htmlcodes as hcodes
from utilities import path
# from restapi.flask_ext.flask_irods.client import IrodsException
from utilities.logs import get_logger

log = get_logger(__name__)
ingestion_user = 'RM'
BACKDOOR_SECRET = 'howdeepistherabbithole'


class IngestionEndpoint(Uploader, EudatEndpoint, ClusterContainerEndpoint):
    """ Create batch folder and upload zip files inside it """

    def get(self, batch_id):

        log.info("Batch request: %s", batch_id)
        # json = {'batch_id': batch_id}
        # msg = prepare_message(
        #     self, json=json, user=ingestion_user, log_string='start')
        # log_into_queue(self, msg)

        ########################
        # get irods session

        # imain = self.get_service_instance(service_name='irods')
        imain = self.get_main_irods_connection()

        batch_path = self.get_irods_batch_path(imain, batch_id)
        local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
        log.info("Batch irods path: %s", batch_path)
        log.info("Batch local path: %s", local_path)

        batch_status, batch_files = self.get_batch_status(imain, batch_path, local_path)

        ########################
        # if not imain.is_collection(batch_path):
        if batch_status == MISSING_BATCH:
            return self.send_errors(
                "Batch '%s' not enabled or you have no permissions"
                % batch_id,
                code=hcodes.HTTP_BAD_NOTFOUND)

        if batch_status == BATCH_MISCONFIGURATION:
            log.error(
                'Misconfiguration: %s files in %s (expected 1)',
                len(batch_files), batch_path)
            return self.send_errors(
                "Misconfiguration for batch_id %s" % batch_id,
                code=hcodes.HTTP_BAD_REQUEST)

        # files = imain.list(batch_path, detailed=True)
        # if len(files) != 1:
        #     return self.send_errors(
        #         "Batch '%s' not yet filled" % batch_id,
        #         code=hcodes.HTTP_BAD_REQUEST)

        # if batch_status == NOT_FILLED_BATCH:
        #     return self.send_errors(
        #         "Batch '%s' not yet filled" % batch_id,
        #         code=hcodes.HTTP_BAD_REQUEST)

        data = {}
        data['batch'] = batch_id
        if batch_status == NOT_FILLED_BATCH:
            data['status'] = 'not_filled'
        elif batch_status == ENABLED_BATCH:
            data['status'] = 'enabled'
        elif batch_status == PARTIALLY_ENABLED_BATCH:
            data['status'] = 'partially_enabled'

        # data['files'] = []
        # for _, f in files.items():
        #     data['files'].append(f)
        data['files'] = batch_files
        return data
        # return "Batch '%s' is enabled and filled" % batch_id

    def post(self, batch_id):
        json_input = self.get_input()

        obj = self.init_endpoint()
        imain = self.get_main_irods_connection()

        batch_path = self.get_irods_batch_path(imain, batch_id)
        log.info("Batch irods path: %s", batch_path)
        local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
        log.info("Batch local path: %s", local_path)

        # Log start (of enable) into RabbitMQ
        log_msg = prepare_message(
            self, json={'batch_id': batch_id},
            user=ingestion_user, log_string='start')
        log_into_queue(self, log_msg)

        # Create the batch folder if not exists
        # Does it already exist?
        # Create the collection and set permissions in irods
        if not imain.is_collection(batch_path):

            imain.create_collection_inheritable(batch_path, obj.username)
        else:
            log.warning("Irods batch collection already exists")

        # Create the folder on filesystem
        if not path.file_exists_and_nonzero(local_path):

            # Create superdirectory and directory on file system:
            try:
                # TODO: REMOVE THIS WHEN path.create() has parents=True!
                import os
                superdir = os.path.join(MOUNTPOINT, INGESTION_DIR)
                if not os.path.exists(superdir):
                    log.debug('Creating %s...', superdir)
                    os.mkdir(superdir)
                    log.info('Created %s...', superdir)
                path.create(local_path, directory=True, force=True)
            except (FileNotFoundError, PermissionError) as e:
                err_msg = ('Could not create directory "%s" (%s)' % (local_path, e))
                log.critical(err_msg)
                log.info('Removing collection from irods (%s)' % batch_path)
                imain.remove(batch_path, recursive=True, force=True)
                return self.send_errors(err_msg, code=hcodes.HTTP_SERVER_ERROR)

        else:
            log.debug("Batch path already exists on filesytem")

        # Log end (of enable) into RabbitMQ
        log_msg = prepare_message(
            self, status='enabled', user=ingestion_user, log_string='end')
        log_into_queue(self, log_msg)

        """
            Download the file into the batch folder
        """

        task = CeleryExt.download_batch.apply_async(
            args=[batch_path, str(local_path), json_input],
            queue='ingestion', routing_key='ingestion'
        )
        log.info("Async job: %s", task.id)
        return self.return_async_id(task.id)

    def delete(self):

        json_input = self.get_input()

        # imain = self.get_service_instance(service_name='irods')
        imain = self.get_main_irods_connection()
        batch_path = self.get_irods_batch_path(imain)
        local_batch_path = str(path.join(MOUNTPOINT, INGESTION_DIR))
        log.debug("Batch collection: %s", batch_path)
        log.debug("Batch path: %s", local_batch_path)

        task = CeleryExt.delete_batches.apply_async(
            args=[batch_path, local_batch_path, json_input],
            queue='ingestion', routing_key='ingestion'
        )
        log.info("Async job: %s", task.id)

        return self.return_async_id(task.id)
