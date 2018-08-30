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

        Example response:
        {
            'batch_id': batch_id,
            'status': 'filled' OR 'exists'
            'description': "Batch 'x' filled"
        }
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
        errors = None

        batch_path = self.get_batch_path(icom, batch_id)
        log.info("Batch path: %s", batch_path)

        ########################
        # Check if the folder exists and is empty
        # Failure: Folder does not exist or no permissions
        # Log to RabbitMQ and return error code
        if not icom.is_collection(batch_path):
            err_msg = ("Batch '%s' not enabled or you have no permissions"
                % batch_id)
            log_msg = prepare_message(self,
                user = ingestion_user,
                log_string = 'failure',
                info = dict(
                    batch_id = batch_id,
                    file_id = file_id,
                    error = err_msg
                )
            )
            log_into_queue(self, log_msg)
            return self.send_errors(err_msg,
                code=hcodes.HTTP_BAD_REQUEST)

        ########################
        # Check for mimetype
        # NOTE: only streaming is allowed, as it is more performant
        ALLOWED_MIMETYPE_UPLOAD = 'application/octet-stream'
        from flask import request

        # Failure: Wrong mimetype:
        # Log to RabbitMQ and return error code
        if request.mimetype != ALLOWED_MIMETYPE_UPLOAD:
            err_msg = ("Only mimetype allowed for upload: %s"
                % ALLOWED_MIMETYPE_UPLOAD)
            log_msg = prepare_message(self,
                user = ingestion_user,
                log_string = 'failure',
                info = dict(
                    batch_id = batch_id,
                    file_id = file_id,
                    error = err_msg
                )
            )
            log_into_queue(self, log_msg)
            return self.send_errors(err_msg,
                code=hcodes.HTTP_BAD_REQUEST)


        ########################
        zip_name = self.get_input_zip_filename(file_id)
        irods_path = self.complete_path(batch_path, zip_name)

        ########################
        # Backdoor: If this is True, the unzip is run directly,
        # and does not have to be called by the qc endpoint!
        backdoor = (file_id == BACKDOOR_SECRET)
        if backdoor and icom.is_dataobject(irods_path): # TODO And if no backdoor?

            response = {
                'batch_id': batch_id,
                'status': 'exists',
                'description': 'A file was uploaded already for this batch.'
            }

            # Log end (of upload) into RabbitMQ
            # In case it already existed!
            log_msg = prepare_message(self,
                user = ingestion_user,
                log_string = 'end', # TODO True?
                status = response['status']
            )
            log_into_queue(self, log_msg)
            return response

        ########################
        # Try to write file into irods
        # NOTE: we know this will always be Compressed Files (binaries)
        # NOTE: permissions are inherited thanks to the POST call
        log.verbose("Cloud filename: %s", irods_path)
        try:
            iout = icom.write_in_streaming(destination=irods_path, force=True)

        # Failure: Streaming into iRODS
        # Log to RabbitMQ and return error code
        except BaseException as e:
            log.error("Failed streaming to iRODS: %s", e)
            err_msg = 'Failed streaming towards B2SAFE cloud'
            log_msg = prepare_message(self,
                user = ingestion_user,
                log_string = 'failure',
                info = dict(
                    batch_id = batch_id,
                    file_id = file_id,
                    error = err_msg
                )
            )
            log_into_queue(self, log_msg)
            return self.send_errors(err_msg,
                code=hcodes.HTTP_SERVER_ERROR)
        else:
            log.info("irods call %s", iout)

        ###########################
        # Also copy file to the B2HOST environment
        log.info('Copying file to B2HOST')

        # Backdoor: Celery task is called to copy file to
        # B2HOST and to unzip.
        if backdoor:
            log.info("Submit async celery task")
            from restapi.flask_ext.flask_celery import CeleryExt
            task = CeleryExt.send_to_workers_task.apply_async(
                args=[batch_id, irods_path, zip_name, backdoor])
            log.warning("Async job: %s", task.id)

        # Normal (no backdoor): Data is copied to B2HOST
        # using a normal container. No unzipping done.
        else:
            rancher = self.get_or_create_handle()
            idest = self.get_ingestion_path()

            b2safe_connvar = {
                'BATCH_SRC_PATH': irods_path,
                'BATCH_DEST_PATH': idest,
                'IRODS_HOST': icom.variables.get('host'),
                'IRODS_PORT': icom.variables.get('port'),
                'IRODS_ZONE_NAME': icom.variables.get('zone'),
                'IRODS_USER_NAME': icom.variables.get('user'),
                'IRODS_PASSWORD': icom.variables.get('password'),
            }

            # Define container
            cname = 'copy_zip'
            cversion = '0.7'  # release 1.0?
            image_tag = '%s:%s' % (cname, cversion)
            container_name = self.get_container_name(batch_id, image_tag)
            docker_image_name = self.get_container_image(
                image_tag, prefix='eudat')

            # Run container
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
        # Finalize response after launching copy to B2HOST
        response = {
            'batch_id': batch_id,
        }

        if errors is None:
            logstring = 'end'
            response['status'] = 'filled'
            response['description'] = "Batch '%s' filled" % batch_id

        else:
            logstring = 'failure'
            if isinstance(errors, dict):
                edict = errors.get('error', {})
                # errors = edict
                # print("TEST", edict)

                # FIXME: Failure or not?
                # Semi-Failure: NotUnique just means that another
                # container of the same name exists! Does this mean
                # failure or not? We cannot even know!!!
                if edict.get('code') == 'NotUnique':
                    response['status'] = 'existing'
                    response['description'] = 'A container of the same name existed, but it is unsure if it was successful. Please delete and retry.'
                    log_msg = prepare_message(self,
                        log_string='failure', # TODO What to say?
                        error = err_msg
                    )
                    log_into_queue(self, log_msg)
                    return self.send_errors(err_msg,
                        code=hcodes.HTTP_BAD_CONFLICT)


                # Failure: Rancher returned errors.
                # Log to RabbitMQ and return error code
                else:
                    err_msg = 'Copy could NOT be started (%s)' % edict
                    log_msg = prepare_message(self,
                        log_string='failure',
                        error = err_msg
                    )
                    log_into_queue(self, log_msg)
                    return self.send_errors(err_msg,
                        code=hcodes.HTTP_SERVER_ERROR)

            # Failure: Unknown error returned by Rancher
            # Log to RabbitMQ and return error code
            else:
                err_msg = 'Unknown error (%s)' % errors
                log_msg = prepare_message(self,
                    log_string='failure',
                    error = err_msg
                )
                log_into_queue(self, log_msg)
                return self.send_errors(err_msg,
                    code=hcodes.HTTP_SERVER_ERROR)

        # Log end (of upload) into RabbitMQ
        log_msg = prepare_message(
            self, status=response['status'],
            user=ingestion_user, log_string=logstring)
        log_into_queue(self, log_msg)

        # Return http=200:
        return self.force_response(response)

    def post(self):
        """
        Create the batch folder if not exists

        Response:
        {
            "batch_id": "xyz",
            "description": "Description of what happened for humans.",
            "status": "enabled" OR "exists"
        }
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

        batch_path = self.get_batch_path(imain, batch_id)
        log.info("Batch path: %s", batch_path)

        # Init response
        response = {
            'batch_id': batch_id
        }

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
            response['description'] = "Batch '%s' enabled" % batch_id
            response['status'] = 'enabled'

        else:
            log.debug("Already exists")
            response['description'] = "Batch '%s' already existed" % batch_id
            response['status'] = 'exists'

        # Log end (of enable) into RabbitMQ
        log_msg = prepare_message(
            self, status=status, user=ingestion_user, log_string='end')
        log_into_queue(self, log_msg)

        return self.force_response(response)
