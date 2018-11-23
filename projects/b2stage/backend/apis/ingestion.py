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

        imain = self.get_service_instance(service_name='irods')
        # obj = self.init_endpoint()
        # icom = obj.icommands

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
                code=hcodes.HTTP_BAD_REQUEST)

        # files = imain.list(batch_path, detailed=True)
        # if len(files) != 1:
        #     return self.send_errors(
        #         "Batch '%s' not yet filled" % batch_id,
        #         code=hcodes.HTTP_BAD_REQUEST)

        if batch_status == NOT_FILLED_BATCH:
            return self.send_errors(
                "Batch '%s' not yet filled" % batch_id,
                code=hcodes.HTTP_BAD_REQUEST)

        if batch_status == BATCH_MISCONFIGURATION:
            log.error(
                'Misconfiguration: %s files in %s (expected 1)',
                len(batch_files), batch_path)
            return self.send_errors(
                "Misconfiguration for batch_id %s" % batch_id,
                code=hcodes.HTTP_BAD_NOTFOUND)

        data = {}
        data['batch'] = batch_id
        if batch_status == ENABLED_BATCH:
            data['status'] = 'enabled'
        elif batch_status == PARTIALLY_ENABLED_BATCH:
            data['status'] = 'partially_enabled'

        # data['files'] = []
        # for _, f in files.items():
        #     data['files'].append(f)
        data['files'] = batch_files
        return data
        # return "Batch '%s' is enabled and filled" % batch_id

    def put(self, batch_id, file_id):
        """
        Let the Replication Manager upload a zip file into a batch folder
        """

        log.info('Received request to upload batch "%s"' % batch_id)

        # Log start (of upload) into RabbitMQ
        log_msg = prepare_message(
            self, json={'batch_id': batch_id, 'file_id': file_id},
            user=ingestion_user, log_string='start')
        log_into_queue(self, log_msg)

        ########################
        # get irods session
        obj = self.init_endpoint()
        icom = obj.icommands

        batch_path = self.get_irods_batch_path(icom, batch_id)
        log.info("Batch path: %s", batch_path)

        ########################
        # Check if the folder exists and is empty
        if not icom.is_collection(batch_path):

            err_msg = ("Batch '%s' not enabled or you have no permissions"
                       % batch_id)
            # Log error into RabbitMQ
            log_msg = prepare_message(
                self, user=ingestion_user,
                log_string='failure',
                info=dict(
                    batch_id=batch_id,
                    file_id=file_id,
                    error=err_msg
                )
            )
            log_into_queue(self, log_msg)

            return self.send_errors(err_msg, code=hcodes.HTTP_BAD_REQUEST)

        ########################
        # NOTE: only streaming is allowed, as it is more performant
        ALLOWED_MIMETYPE_UPLOAD = 'application/octet-stream'
        from flask import request
        if request.mimetype != ALLOWED_MIMETYPE_UPLOAD:
            return self.send_errors(
                "Only mimetype allowed for upload: %s"
                % ALLOWED_MIMETYPE_UPLOAD,
                code=hcodes.HTTP_BAD_REQUEST)

        ########################
        backdoor = file_id == BACKDOOR_SECRET
        response = {
            'batch_id': batch_id,
            'status': 'filled',
        }

        ########################
        zip_name = self.get_input_zip_filename(file_id)
        zip_path_irods = self.complete_path(batch_path, zip_name)
        # E.g. /myIrodsZone/batches/<batch_id>/<zip-name>

        # This path is created by the POST method, important to keep this check here
        if backdoor and icom.is_dataobject(zip_path_irods):
            response['status'] = 'exists'

            # Log end (of upload) into RabbitMQ
            # In case it already existed!
            log_msg = prepare_message(
                self,
                user=ingestion_user,
                log_string='end',  # TODO True?
                status=response['status']
            )
            log_into_queue(self, log_msg)
            return response

        ########################
        log.verbose("Cloud path: %s", zip_path_irods)  # ingestion

        local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
        path.create(local_path, directory=True, force=True)
        zip_path = path.join(local_path, zip_name)
        log.info("Local path: %s", zip_path)

        # try:
        #     # NOTE: we know this will always be Compressed Files (binaries)
        #     iout = icom.write_in_streaming(destination=zip_path_irods, force=True)
        # except BaseException as e:
        #     log.error("Failed streaming to iRODS: %s", e)
        #     return self.send_errors(
        #         "Failed streaming towards B2SAFE cloud",
        #         code=hcodes.HTTP_SERVER_ERROR)
        # else:
        #     log.info("irods call %s", iout)
        #     # NOTE: permissions are inherited thanks to the POST call

        try:
            # NOTE: we know this will always be Compressed Files (binaries)
            out = self.upload_chunked(destination=zip_path, force=True)
        except BaseException as e:
            log.error("Failed streaming to %s: %s", str(zip_path), e)
            return self.send_errors(
                "Failed streaming zip path to file system",
                code=hcodes.HTTP_SERVER_ERROR)
        else:
            log.info("File uploaded: %s", out)

        log.info("Submit async celery task")
        # task = CeleryExt.copy_from_b2safe_to_b2host.apply_async(
        task = CeleryExt.copy_from_b2host_to_b2safe.apply_async(
            args=[batch_id, zip_path_irods, str(zip_path), backdoor])
        log.warning("Async job: %s", task.id)

        # Log end (of upload) into RabbitMQ
        log_msg = prepare_message(
            self, status=response['status'],
            user=ingestion_user, log_string='end')
        log_into_queue(self, log_msg)

        # return self.force_response(response)
        return self.return_async_id(task.id)

    def post(self):
        """
        Create the batch folder if not exists
        """

        param_name = 'batch_id'
        self.get_input()
        batch_id = self._args.get(param_name, None)

        if batch_id is None:
            return self.send_errors(
                "Mandatory parameter '%s' missing" % param_name,
                code=hcodes.HTTP_BAD_REQUEST)

        log.info('Received request to enable batch "%s"' % batch_id)

        # Log start (of enable) into RabbitMQ
        log_msg = prepare_message(
            self, json={'batch_id': batch_id},
            user=ingestion_user, log_string='start')
        log_into_queue(self, log_msg)

        ##################
        # Get irods session
        obj = self.init_endpoint()
        # icom = obj.icommands

        # NOTE: Main API user is the key to let this happen
        imain = self.get_service_instance(service_name='irods')

        batch_path = self.get_irods_batch_path(imain, batch_id)
        log.info("Batch path: %s", batch_path)

        ##################
        # Does it already exist? Is it a collection?
        if not imain.is_collection(batch_path):
            # Enable the batch
            batch_path = self.get_irods_batch_path(imain, batch_id)
            # Create the path and set permissions
            imain.create_collection_inheritable(batch_path, obj.username)
            # # Remove anonymous access to this batch
            # ianonymous.set_permissions(
            #     batch_path,
            #     permission='null', userOrGroup=icom.anonymous_user)
            local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
            path.create(local_path, directory=True, force=True)

            ##################
            response = "Batch '%s' enabled" % batch_id
            status = 'enabled'

        else:
            log.debug("Already exists")
            response = "Batch '%s' already exists" % batch_id
            status = 'exists'

        # Log end (of enable) into RabbitMQ
        log_msg = prepare_message(
            self, status=status, user=ingestion_user, log_string='end')
        log_into_queue(self, log_msg)

        return self.force_response(response)

    def delete(self):

        json_input = self.get_input()

        imain = self.get_service_instance(service_name='irods')
        batch_path = self.get_irods_batch_path(imain)
        log.debug("Batch path: %s", batch_path)

        task = CeleryExt.delete_batches.apply_async(
            args=[batch_path, json_input]
        )
        log.warning("Async job: %s", task.id)
        return self.return_async_id(task.id)
