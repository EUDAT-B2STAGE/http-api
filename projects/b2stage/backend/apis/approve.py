# -*- coding: utf-8 -*-

"""
Endpoint example for the RAPyDo framework
"""

#################
# IMPORTS
from restapi.rest.definition import EndpointResource
from utilities import htmlcodes as hcodes
# from restapi.services.detect import detector
from utilities.logs import get_logger

#################
# INIT VARIABLES
log = get_logger(__name__)


#################
# REST CLASS
class Approve(EndpointResource):

    def get(self, batch_id):
        log.info("Received a test HTTP request")
        # self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')
        response = 'Dummy method.'
        return self.force_response(response)

    def post(self, batch_id):

        log.info("Received a test HTTP request")

        ################
        json_input = self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')  # UHM!
        print(self._args)
        key_json_parameter = 'files_list'
        if key_json_parameter not in json_input:
            return self.send_errors(
                'Missing parameter: %s' % key_json_parameter,
                code=hcodes.HTTP_BAD_REQUEST
            )
        else:
            flist = json_input.get(key_json_parameter)
            if not isinstance(flist, list) or len(flist) < 1:
                return self.send_errors(
                    "Parameter '%s' " % key_json_parameter +
                    "should be a list of file names " +
                    "(with at least one file)",
                    code=hcodes.HTTP_BAD_REQUEST
                )

        ################
        response = 'Dummy method. File list received: %s' % flist
        return self.force_response(response)
