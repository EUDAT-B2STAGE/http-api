# -*- coding: utf-8 -*-

"""
Ingestion process submission to upload the SeaDataNet marine data.
"""

from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi.services.uploader import Uploader
# from restapi.rest.definition import EndpointResource
# from b2stage.apis.commons.seadatacloud import SEADATA_ENABLED
from utilities import htmlcodes as hcodes
from restapi.services.detect import detector
from utilities.logs import get_logger

log = get_logger(__name__)
BATCHES_DIR = detector.get_global_var('SEADATA_BATCH_DIR')


class IngestionEndpoint(Uploader, EudatEndpoint):
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

        #######################
        # Upload the file to temporary location

        # Read the request
        from flask import request
        request.get_data()
        # Normal upload: inside the host tmp folder
        response = super(IngestionEndpoint, self) \
            .upload(subfolder=obj.username, force=True)
        # Check if upload response is success
        content, errors, status = self.explode_response(response, get_all=True)

        key_file = 'filename'
        if isinstance(content, dict) and key_file in content:
            original_filename = content[key_file]
            fpath = self.absolute_upload_file(original_filename, obj.username)
            log.info("File is '%s'" % fpath)
        else:
            return self.send_errors(errors=errors, code=status)

        #######################
        # Complain if this is not the wanted extension
        # TODO: see how to do it in Python
        # if extension not in self._allowed_extensions

        #######################
        # Put it into iRODS with a fixed name
        ipath = self.complete_path(batch_path, batch_id + '.zip')
        icom.save(fpath, destination=ipath, force=True)
        log.verbose("Stored: %s", ipath)

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
        # Does it already exist?

        # Is it a collection?
        # if icom.is_collection(location):

        # Are the permissions fine?

        ##################
        batch_path = self.get_batch_path(icom, batch_id)
        ianonymous = self.get_service_instance(
            service_name='irods', user=icom.anonymous_user, password='null')
        # Create the path
        ianonymous.create_empty(
            batch_path, directory=True, ignore_existing=True)
        # This user will own the directory
        ianonymous.set_permissions(
            batch_path, permission='own', userOrGroup=obj.username)
        # Remove anonymous access to this batch
        ianonymous.set_permissions(
            batch_path, permission='null', userOrGroup=icom.anonymous_user)

        ##################
        response = "Batch '%s' enabled" % batch_id
        return self.force_response(response)
