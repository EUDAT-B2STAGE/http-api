# -*- coding: utf-8 -*-

"""
Ingestion process submission to upload the SeaDataNet marine data.
"""

from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi.services.uploader import Uploader
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from utilities import htmlcodes as hcodes
from restapi.services.detect import detector
from utilities.logs import get_logger

log = get_logger(__name__)
BATCHES_DIR = detector.get_global_var('SEADATA_BATCH_DIR')


class IngestionEndpoint(Uploader, EudatEndpoint, ClusterContainerEndpoint):
    """ Create batch folder and upload zip files inside it """

    _allowed_extensions = ['zip']

    def get_batch_path(self, icom, batch_id=None):

        # home_dir = icom.get_home_var()
        paths = [BATCHES_DIR]
        if batch_id is not None:
            paths.append(batch_id)
        from utilities import path
        suffix_path = str(path.build(paths))

        return icom.get_current_zone(suffix=suffix_path)

    def get(self, batch_id):

        ########################
        # get irods session
        obj = self.init_endpoint()
        icom = obj.icommands

        batch_path = self.get_batch_path(icom, batch_id)
        log.info("Batch path: %s", batch_path)

        ########################
        # Check if the folder exists and is empty
        if not icom.is_collection(batch_path):
            return self.send_errors(
                "Batch '%s' not enabled or you have no permissions"
                % batch_id,
                code=hcodes.HTTP_BAD_REQUEST)

        files = icom.list(batch_path)
        if len(files) != 1:
            return self.send_errors(
                "Batch '%s' not yet filled" % batch_id,
                code=hcodes.HTTP_BAD_REQUEST)

        return "Batch '%s' is enabled and filled" % batch_id

    def put(self, batch_id):
        """
        Let the Replication Manager upload a zip file into a batch folder
        """

        ########################
        # get irods session
        obj = self.init_endpoint()
        icom = obj.icommands

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

        ipath = self.complete_path(batch_path, 'input.zip')
        try:
            iout = icom.write_in_streaming(destination=ipath, force=True)
        except BaseException as e:
            log.error("Failed streaming to iRODS: %s", e)
            return self.send_errors(
                "Failed streaming towards B2SAFE cloud",
                code=hcodes.HTTP_SERVER_ERROR)
        else:
            log.info("irods call %s", iout)
            # NOTE: permissions are inherited thanks to the POST call

        # ###########################
        # # Also copy file to the B2HOST environment

        # b2safe_connvar = {
        #     # TODO: test icom.variables please
        #     # 'IRODS_HOST': icom.variables.get('host'),
        #     # 'IRODS_PORT': icom.variables.get('port'),
        #     # 'IRODS_ZONE_NAME': icom.variables.get('zone'),
        #     # 'IRODS_USER_NAME': icom.variables.get('user'),
        #     # 'IRODS_PASSWORD': icom.variables.get('password'),
        # }

        # rancher = self.get_or_create_handle()
        # cname = 'copy_zip'
        # cversion = '0.5'
        # image_tag = '%s:%s' % (cname, cversion)
        # container_name = self.get_container_name(batch_id, image_tag)
        # docker_image_name = self.get_container_image(image_tag, prefix='eudat')
        # errors = rancher.run(
        #     container_name=container_name, image_name=docker_image_name,
        #     private=True, extras={'environment': b2safe_connvar},
        # )

        # errors
        # # if errors is not None:
        # #     if isinstance(errors, dict):
        # #         edict = errors.get('error', {})
        # #         # print("TEST", edict)
        # #         if edict.get('code') == 'NotUnique':
        # #             response['status'] = 'existing'
        # #         else:
        # #             response['status'] = 'could NOT be started'
        # #             response['description'] = edict
        # #     else:
        # #         response['status'] = 'failure'

        ########################
        response = "Batch '%s' filled" % batch_id
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

        # get irods session
        obj = self.init_endpoint()
        icom = obj.icommands

        batch_path = self.get_batch_path(icom, batch_id)
        log.info("Batch path: %s", batch_path)

        ##################
        # FIXME: possible questions:
        # Does it already exist?
        # Is it a collection? # if icom.is_collection(location):
        # Are the permissions fine?

        ##################
        # Enable the batch with the right permissions
        # NOTE: Main API user is the key to let this happen

        imain = self.get_service_instance(service_name='irods')
        # ianonymous = self.get_service_instance(
        #     service_name='irods', user=icom.anonymous_user, password='null')

        # Create the path
        batch_path = self.get_batch_path(icom, batch_id)
        imain.create_empty(batch_path, directory=True, ignore_existing=True)
        # This user will own the directory
        imain.set_permissions(
            batch_path,
            permission='own', userOrGroup=obj.username)
        # Let the permissions scale to subelements
        imain.enable_inheritance(batch_path)  # cool!

        # # # Remove anonymous access to this batch
        # # ianonymous.set_permissions(
        # #     batch_path, permission='null', userOrGroup=icom.anonymous_user)

        ##################
        response = "Batch '%s' enabled" % batch_id
        return self.force_response(response)
