# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.

Code to implement the extended endpoints

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/metadata_parser/docs/user/endpoints.md

"""

from rapydo.rest.definition import EndpointResource
from rapydo.utils import htmlcodes as hcodes
from b2handle.handleclient import EUDATHandleClient
from b2handle import handleexceptions

from rapydo.utils.logs import get_logger

log = get_logger(__name__)


###############################
# Classes

class PIDEndpoint(EndpointResource):

    def get(self, pid=None):
        """ Get file from pid """
        print("*******************-> ", pid)
        if pid is None:
            return self.send_errors(
                message='Missing PID inside URI',
                code=hcodes.HTTP_BAD_REQUEST)

        ###################
        # Perform B2HANDLE request: retrieve URL from handle
        ###################
        value = None
        client = EUDATHandleClient.instantiate_for_read_access()
        try:
            value = client.get_value_from_handle(pid, "URL")
            pass
        except handleexceptions.HandleSyntaxError as e:
            errorMessage = "B2HANDLE: %s" % str(
                e)
            log.critical(errorMessage)
            return self.send_errors(
                message=errorMessage, code=hcodes.HTTP_BAD_REQUEST)
        except handleexceptions.HandleNotFoundException as e:
            errorMessage = "B2HANDLE: %s" % str(
                e)
            log.critical(errorMessage)
            return self.send_errors(
                message=errorMessage, code=hcodes.HTTP_BAD_NOTFOUND)
        if value is None:
            return self.send_errors(
                message='B2HANDLE empty value returned',
                code=hcodes.HTTP_BAD_NOTFOUND)

        #################
        # If downlaod is True, trigger file download
        ##################
        if self._args.get('download'):
            pass

        return value
