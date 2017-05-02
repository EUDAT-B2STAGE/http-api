# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.

Code to implement the extended endpoints

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/metadata_parser/docs/user/endpoints.md

"""

from flask import request, current_app
from flask_ext.flask_irods.client import IrodsException
from eudat.apis.common.b2stage import EudatEndpoint

from rapydo.services.uploader import Uploader
from rapydo.utils import htmlcodes as hcodes
from rapydo import decorators as decorate
from b2handle.handleclient import EUDATHandleClient
from b2handle import handleexceptions

from rapydo.utils.logs import get_logger

log = get_logger(__name__)


###############################
# Classes

class PIDEndpoint(Uploader, EudatEndpoint):

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, pid=None):
        """ Get file from pid """
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
            log.info("B2HANDLE response: %s", value)
        except handleexceptions.HandleSyntaxError as e:
            errorMessage = "B2HANDLE: %s" % str(e)
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

        
        # If downlaod is True, trigger file download
        parameters = self.get_input()
        if (parameters.download and 'true' in parameters.download):

            from rapydo.confs import get_api_url
            api_url = get_api_url()

            #For testing pourpose, then to be removed
            value = 'apiserver.dockerized.io:5000/api/namespace/tempZone/home/guest/gettoken'
            #value = 'apiserver.dockerized.io:5000/api/namespace/tempZone/home/guest/invalid'

            # If local HTTP-API perform a direct download
            # TO FIX: the following code can be improved
            route = api_url + 'api/namespace/'
            route = route.replace('http://' , '')
            
            if (value.startswith(route)): 
                value = value.replace(route, '/')
                r = self.init_endpoint()
                if r.errors is not None:
                    return self.send_errors(errors=r.errors)
                icom = r.icommands
                value = self.download_object(r, value)
            else:
                # Perform a request to an external service?
                return self.send_errors(
                message='PID was correctly resolved in \'' + value + 
                '\', but can not be downloaded by this HTTP-API server \'' +
                route + '\'', code=hcodes.HTTP_BAD_UNAUTHORIZED)

        return value
