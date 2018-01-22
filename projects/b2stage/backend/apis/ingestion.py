# -*- coding: utf-8 -*-

"""
Ingestion process submission to upload the SeaDataNet marine data.
"""

from b2stage.apis.commons.endpoint import EudatEndpoint
# from restapi.rest.definition import EndpointResource
from utilities.logs import get_logger
# from b2stage.apis.commons.seadatacloud import SEADATA_ENABLED

log = get_logger(__name__)


class Ingestion(EudatEndpoint):
    """ Create batch folder and upload zip files inside it """

    def get_batch_path(self, icom, batch_id):

        from utilities import path
        suffix_path = str(path.build(['batchs', batch_id]))
        return icom.get_current_zone(suffix=suffix_path)

    def put(self, batch_id):
        """
        Create the batch folder if not exists
        """

        obj = self.init_endpoint()
        path = self.get_batch_path(obj.icommands, batch_id)
        log.info("Batch path: %s", path)

        response = 'Hello world!'
        return self.force_response(response)

    def post(self):
        """
        Let the Replication Manager upload a zip file into a batch folder
        """

        # NOTE: should I check if the folder is empty and give error otherwise?

        response = 'Hello world!'
        return self.force_response(response)

        # # Parse input parameters:
        # # NOTE: they can be caught only if indicated in swagger files
        # self.get_input()
        # # pretty print arguments obtained from the _args private attribute
        # log.pp(self._args, prefix_line='Parsed args')

        # # Activate a service handle
        # service_handle = self.get_service_instance(service_name)

        # # Handle errors
        # if service_handle is None:
        #     log.error('Service %s unavailable', service_name)
        #     return self.send_errors(
        #         message='Server internal error. Please contact adminers.',
        #         # code=hcodes.HTTP_BAD_NOTFOUND
        #     )
