# -*- coding: utf-8 -*-

"""
Ingestion process submission to upload the SeaDataNet marine data.
"""

from b2stage.apis.commons.endpoint import EudatEndpoint
# from restapi.rest.definition import EndpointResource
# from b2stage.apis.commons.seadatacloud import SEADATA_ENABLED
from utilities import htmlcodes as hcodes
from restapi.services.detect import detector
from utilities.logs import get_logger

log = get_logger(__name__)
BATCHES_DIR = detector.get_global_var('SEADATA_BATCH_DIR')


class Ingestion(EudatEndpoint):
    """ Create batch folder and upload zip files inside it """

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

        # NOTE: should I check if the folder is empty and give error otherwise?

        response = 'Hello world!'
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
