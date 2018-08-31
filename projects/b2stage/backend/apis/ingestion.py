# -*- coding: utf-8 -*-

"""
Ingestion process submission to upload the SeaDataNet marine data.
"""

from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi.services.uploader import Uploader
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from b2stage.apis.commons.queue import *
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
        taskname = 'upload'
        json_input = self.get_input() # call only once
        log_start(self, taskname, json_input)

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
            log.warn(err_msg)
            log_failure(self, taskname, json_input, err_msg)
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
            log.warn(err_msg)
            log_failure(self, taskname, json_input, err_msg)
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

            desc = 'A file was uploaded already for this batch.'
            status = 'exists'
            response = {
                'batch_id': batch_id,
                'status': status,
                'description': desc
            }
            log_success(self, taskname, json_input, status, desc)

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
            log_failure(self, taskname, json_input, err_msg)
            return self.send_errors(err_msg,
                code=hcodes.HTTP_SERVER_ERROR)
        else:
            log.info("irods call %s", iout)
            log_progress(self, taskname, json_input, 'Data streamed to irods.')

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

            response = {
                'batch_id': batch_id,
                'status': 'submitted',
                'async': task.id,
                'description': 'Launched asynchronous celery task for copying data to B2HOST.'
            }
            log_submitted(self, taskname, json_input, task.id)

            # Return http=200:
            return self.force_response(response)

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
        if errors is not None:
            response = {
                'batch_id': batch_id,
            }
            log.error('Rancher: %s', errors)
            if isinstance(errors, dict):
                edict = errors.get('error', {})

                # FIXME: Failure or not?
                # Semi-Failure: NotUnique just means that another
                # container of the same name exists! Does this mean
                # failure or not? We cannot even know!!!
                if edict.get('code') == 'NotUnique':
                    response['status'] = 'existing'
                    err_msg = 'A container of the same name existed, but it is unsure if it was successful. Please delete and retry.'
                    response['description'] = err_msg
                    log.warn(err_msg)
                    log_failure(self, taskname, json_input, err_msg)
                    return self.send_errors(err_msg,
                        code=hcodes.HTTP_BAD_CONFLICT)


                # Failure: Rancher returned errors.
                # Log to RabbitMQ and return error code
                else:
                    err_msg = 'Copy could NOT be started (%s)' % edict
                    log.warn(err_msg)
                    log_failure(self, taskname, json_input, err_msg)
                    return self.send_errors(err_msg,
                        code=hcodes.HTTP_SERVER_ERROR)

            # Failure: Unknown error returned by Rancher
            # Log to RabbitMQ and return error code
            else:
                err_msg = 'Upload: Unknown error (%s)' % errors
                log.warn(err_msg)
                log_failure(self, taskname, json_input, err_msg)
                return self.send_errors(err_msg,
                    code=hcodes.HTTP_SERVER_ERROR)

        # If everything went well:
        response = {
            'batch_id': batch_id,
            'status': 'filled', # TODO: Or 'launched'? We cannot be sure, as the container was only launched.
            'description': "Batch '%s' filled" % batch_id
        }

        # Log end (of upload) into RabbitMQ
        desc = ('Launched the container %s (%s), but unsure if it succeeded.'
            % (container_name, docker_image_name))
        log_success_uncertain(self, taskname, json_input, desc)

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
        json_input = self.get_input() # call only once
        #batch_id = self._args.get(param_name, None)
        batch_id = json_input['batch_id'] if 'batch_id' in json_input else None

        if batch_id is None:
            return self.send_errors(
                "Mandatory parameter '%s' missing" % param_name,
                code=hcodes.HTTP_BAD_REQUEST)

        # Log start (of enable) into RabbitMQ
        log.info('Received request to enable batch "%s"' % batch_id)
        #json_input = self.get_input() # call only once
        taskname = 'enable'
        log_start(self, taskname, json_input)

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
            desc = ("Batch '%s' enabled" % batch_id)
            status = 'enabled'

        else:
            log.debug("Already exists")
            desc = ("Batch '%s' already existed" % batch_id)
            status = 'exists'

        # Init response
        response = {
            'batch_id': batch_id,
            'status': status,
            'description' : desc
        }
        # Log end (of enable) into RabbitMQ
        log_success(self, taskname, json_input, status, desc)
        return self.force_response(response)
