# -*- coding: utf-8 -*-

"""
Ingestion process submission to upload the SeaDataNet marine data.
"""

from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi.services.uploader import Uploader
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from b2stage.apis.commons.queue import log_into_queue, prepare_message
from utilities import htmlcodes as hcodes
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

        batch_path = self.get_batch_path(imain, batch_id)
        log.info("Batch path: %s", batch_path)

        ########################
        # Check if the folder exists and is empty
        if not imain.is_collection(batch_path):
            return self.send_errors(
                "Batch '%s' not enabled or you have no permissions"
                % batch_id,
                code=hcodes.HTTP_BAD_REQUEST)

        files = imain.list(batch_path)
        # log.pp(files)
        # if len(files) < 1:
        if len(files) != 1:
            return self.send_errors(
                "Batch '%s' not yet filled" % batch_id,
                code=hcodes.HTTP_BAD_REQUEST)

        return "Batch '%s' is enabled and filled" % batch_id

    def put(self, batch_id, file_id):
        """
        Let the Replication Manager upload a zip file into a batch folder
        """

        ##################
        msg = prepare_message(
            self, json={'batch_id': batch_id, 'file_id': file_id},
            user=ingestion_user, log_string='start')
        log_into_queue(self, msg)

        ########################
        # get irods session
        obj = self.init_endpoint()
        icom = obj.icommands
        errors = None

        batch_path = self.get_batch_path(icom, batch_id)
        log.info("Batch path: %s", batch_path)

        ########################
        # Check if the folder exists and is empty
        if not icom.is_collection(batch_path):
            return self.send_errors(
                "Batch '%s' not enabled or you have no permissions"
                % batch_id,
                code=hcodes.HTTP_BAD_REQUEST)

        ########################
        # NOTE: only streaming is allowed, as it is more performant
        ALLOWED_MIMETYPE_UPLOAD = 'application/octet-stream'
        from flask import request
        if request.mimetype != ALLOWED_MIMETYPE_UPLOAD:
            return self.send_errors(
                "Only mimetype allowed for upload: %s"
                % ALLOWED_MIMETYPE_UPLOAD,
                code=hcodes.HTTP_BAD_REQUEST)

        zip_name = self.get_input_zip_filename(file_id)
        ipath = self.complete_path(batch_path, zip_name)
        log.verbose("Cloud filename: %s", ipath)
        try:
            # NOTE: we know this will always be Compressed Files (binaries)
            iout = icom.write_in_streaming(
                destination=ipath, force=True, binary=True)
        except BaseException as e:
            log.error("Failed streaming to iRODS: %s", e)
            return self.send_errors(
                "Failed streaming towards B2SAFE cloud",
                code=hcodes.HTTP_SERVER_ERROR)
        else:
            log.info("irods call %s", iout)
            # NOTE: permissions are inherited thanks to the POST call

        ###########################
        # Also copy file to the B2HOST environment

        backdoor = file_id == BACKDOOR_SECRET
        if backdoor:
            # # CELERY VERSION
            log.info("Submit async celery task")
            from restapi.flask_ext.flask_celery import CeleryExt
            task = CeleryExt.send_to_workers_task.apply_async(
                args=[batch_id, ipath, zip_name, backdoor], countdown=10
            )
            log.warning("Async job: %s", task.id)
        else:
            # # CONTAINERS VERSION
            rancher = self.get_or_create_handle()
            idest = self.get_ingestion_path()

            b2safe_connvar = {
                'BATCH_SRC_PATH': ipath,
                'BATCH_DEST_PATH': idest,
                'IRODS_HOST': icom.variables.get('host'),
                'IRODS_PORT': icom.variables.get('port'),
                'IRODS_ZONE_NAME': icom.variables.get('zone'),
                'IRODS_USER_NAME': icom.variables.get('user'),
                'IRODS_PASSWORD': icom.variables.get('password'),
            }

            # Launch a container to copy the data into B2HOST
            cname = 'copy_zip'
            cversion = '0.7'  # release 1.0?
            image_tag = '%s:%s' % (cname, cversion)
            container_name = self.get_container_name(batch_id, image_tag)
            docker_image_name = self.get_container_image(
                image_tag, prefix='eudat')
            log.info("Requesting copy: %s" % docker_image_name)
            errors = rancher.run(
                container_name=container_name, image_name=docker_image_name,
                private=True, pull=False,
                extras={
                    'environment': b2safe_connvar,
                    'dataVolumes': [self.mount_batch_volume(batch_id)],
                },
            )

        ########################
        response = {
            'batch_id': batch_id,
            'status': 'filled',
        }

        if errors is not None:
            if isinstance(errors, dict):
                edict = errors.get('error', {})
                # errors = edict
                # print("TEST", edict)
                if edict.get('code') == 'NotUnique':
                    response['status'] = 'existing'
                else:
                    response['status'] = 'Copy could NOT be started'
                    response['description'] = edict
            else:
                response['status'] = 'failure'
        response['errors'] = errors
        response = "Batch '%s' filled" % batch_id

        msg = prepare_message(
            self, status=response['status'],
            user=ingestion_user, log_string='end')
        log_into_queue(self, msg)

        return self.force_response(response)

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

        ##################
        msg = prepare_message(
            self, json={'batch_id': batch_id},
            user=ingestion_user, log_string='start')
        log_into_queue(self, msg)

        ##################
        # Get irods session
        obj = self.init_endpoint()
        # icom = obj.icommands

        # NOTE: Main API user is the key to let this happen
        imain = self.get_service_instance(service_name='irods')

        batch_path = self.get_batch_path(imain, batch_id)
        log.info("Batch path: %s", batch_path)

        ##################
        # Does it already exist? Is it a collection?
        if not imain.is_collection(batch_path):
            # Enable the batch
            batch_path = self.get_batch_path(imain, batch_id)
            # Create the path and set permissions
            imain.create_collection_inheritable(batch_path, obj.username)
            # # Remove anonymous access to this batch
            # ianonymous.set_permissions(
            #     batch_path,
            #     permission='null', userOrGroup=icom.anonymous_user)

            ##################
            response = "Batch '%s' enabled" % batch_id
            status = 'enabled'

        else:
            log.debug("Already exists")
            response = "Batch '%s' already exists" % batch_id
            status = 'exists'

        ##################
        msg = prepare_message(
            self, status=status, user=ingestion_user, log_string='end')
        log_into_queue(self, msg)
        return self.force_response(response)
