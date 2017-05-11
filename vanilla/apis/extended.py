# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.

Code to implement the extended endpoints

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/metadata_parser/docs/user/endpoints.md

"""

import os
# from flask import request, current_app
from flask_ext.flask_irods.client import IrodsException
from eudat.apis.common import CURRENT_HTTPAPI_SERVER  # , PRODUCTION
from eudat.apis.common.b2stage import EudatEndpoint

from rapydo.services.uploader import Uploader
from rapydo.utils import htmlcodes as hcodes
from rapydo import decorators as decorate
from b2handle.handleclient import EUDATHandleClient
from b2handle.clientcredentials import PIDClientCredentials
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
        URL_value = None
        CHECKSUM_value = None
        credentials_file = os.environ.get('HANDLE_CREDENTIALS')
        if credentials_file and os.path.isfile(credentials_file):
            cred = PIDClientCredentials.load_from_JSON(credentials_file)
            client = EUDATHandleClient.instantiate_with_credentials(cred)
        else:
            if credentials_file and not os.path.isfile(credentials_file):
                log.critical("B2HANDLE credentials file not found %s",
                             credentials_file)
            client = EUDATHandleClient.instantiate_for_read_access()
        try:
            URL_value = client.get_URL_value_from_handle(pid, "URL")
            CHECKSUM_value = client.get_URL_value_from_handle(
                                 pid, "EUDAT/CHECKSUM")
            log.info("B2HANDLE response: %s", URL_value)
        except handleexceptions.HandleSyntaxError as e:
            errorMessage = "B2HANDLE: %s" % str(e)
            log.warning(errorMessage)
            return self.send_errors(
                message=errorMessage, code=hcodes.HTTP_BAD_REQUEST)
        except handleexceptions.HandleNotFoundException as e:
            errorMessage = "B2HANDLE: %s" % str(
                e)
            log.critical(errorMessage)
            return self.send_errors(
                message=errorMessage, code=hcodes.HTTP_BAD_NOTFOUND)
        if URL_value is None:
            return self.send_errors(
                message='B2HANDLE empty URL_value returned',
                code=hcodes.HTTP_BAD_NOTFOUND)

        # If downlaod is True, trigger file download
        if hasattr(self._args, 'download'):
            if self._args.download and 'true' in self._args.download.lower():

                api_url = CURRENT_HTTPAPI_SERVER

                # TODO: check download in debugging mode
                # if not PRODUCTION:
                #     # For testing pourpose, then to be removed
                #     URL_value = CURRENT_HTTPAPI_SERVER + \
                #         '/api/namespace/tempZone/home/guest/gettoken'

                # If local HTTP-API perform a direct download
                # TO FIX: the following code can be improved
                route = api_url + 'api/registered/'
                # route = route.replace('http://', '')

                if (URL_value.startswith(route)):
                    URL_value = URL_value.replace(route, '/')
                    r = self.init_endpoint()
                    if r.errors is not None:
                        return self.send_errors(errors=r.errors)
                    URL_value = self.download_object(r, URL_value)
                else:
                    # Perform a request to an external service?
                    return self.send_warnings(
                        {'url': URL_value},
                        errors=[
                            "Data-object can't be downloaded by current " +
                            "HTTP-API server '%s'" % api_url
                        ]
                    )
            return URL_value
        else:
            return {'url': URL_value, 'EUDAT/CHECKSUM': CHECKSUM_value}
