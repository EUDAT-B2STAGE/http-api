# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.

Code to implement the extended endpoints

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/metadata_parser/docs/user/endpoints.md

"""

import os
from restapi.flask_ext.flask_irods.client import IrodsException
from b2stage.apis.commons import CURRENT_HTTPAPI_SERVER  # , PRODUCTION
from b2stage.apis.commons.endpoint import EudatEndpoint

from restapi.services.uploader import Uploader
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate
from b2handle.handleclient import EUDATHandleClient
from b2handle.clientcredentials import PIDClientCredentials
from b2handle import handleexceptions

from utilities.logs import get_logger

log = get_logger(__name__)


###############################
# Classes

class PIDEndpoint(Uploader, EudatEndpoint):

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, pid=None):
        """ Get metadata or file from pid """

        if pid is None:
            return self.send_errors(
                message='Missing PID inside URI',
                code=hcodes.HTTP_BAD_REQUEST)

        # parse query parameters
        self.get_input()

        ###################
        # Perform B2HANDLE request: retrieve URL from handle
        # TOFIX: move the PID part inside a http-api-base class
        ###################
        self.URL_value = None
        self.CHECKSUM_value = None
        self.UNPUBLISHED_value = None
        self.UNPUBLISHED_DATE_value = None
        self.UNPUBLISHED_REASON_value = None

        credentials_file = os.environ.get('HANDLE_CREDENTIALS')
        credentials_found = False

        if credentials_file:
            if os.path.isfile(credentials_file):
                credentials_found = True
            else:
                log.critical("B2HANDLE credentials file not found %s",
                             credentials_file)

        if credentials_found:
            cred = PIDClientCredentials.load_from_JSON(credentials_file)
            client = EUDATHandleClient.instantiate_with_credentials(cred)
            response = self.get_pid_fields(client, pid)
            if response:
                return response

        if self.URL_value is None:
            return self.send_errors(
                message='B2HANDLE empty URL_value returned',
                code=hcodes.HTTP_BAD_NOTFOUND)

        # If downlaod is True, trigger file download
        if (hasattr(self._args, 'download')):
            if self._args.download and 'true' in self._args.download.lower():

                api_url = CURRENT_HTTPAPI_SERVER

                # TODO: check download in debugging mode
                # if not PRODUCTION:
                #     # For testing pourpose, then to be removed
                #     URL_value = CURRENT_HTTPAPI_SERVER + \
                #         '/api/namespace/tempZone/home/guest/gettoken'

                # If local HTTP-API perform a direct download
                # TOFIX: the following code can be improved
                route = api_url + 'api/registered/'
                # route = route.replace('http://', '')

                if (self.URL_value.startswith(route)):
                    self.URL_value = self.URL_value.replace(route, '/')
                    r = self.init_endpoint()
                    if r.errors is not None:
                        return self.send_errors(errors=r.errors)
                    self.URL_value = self.download_object(r, self.URL_value)
                else:
                    # Perform a request to an external service?
                    return self.send_warnings(
                        {'URL': self.URL_value},
                        errors=[
                            "Data-object can't be downloaded by current " +
                            "HTTP-API server '%s'" % api_url
                        ]
                    )
                return self.URL_value

        return {'URL': self.URL_value, 'EUDAT/CHECKSUM': self.CHECKSUM_value,
                'EUDAT/UNPUBLISHED': self.UNPUBLISHED_value,
                'EUDAT/UNPUBLISHED_DATE': self.UNPUBLISHED_DATE_value,
                'EUDAT/UNPUBLISHED_REASON': self.UNPUBLISHED_REASON_value}

    def get_pid_fields(self, client, pid):
        try:
            self.URL_value = client.get_value_from_handle(pid, "URL")
            self.CHECKSUM_value = client.get_value_from_handle(
                pid, "EUDAT/CHECKSUM")
            self.UNPUBLISHED_value = client.get_value_from_handle(
                pid, "EUDAT/UNPUBLISHED")
            self.UNPUBLISHED_DATE_value = client.get_value_from_handle(
                pid, "EUDAT/UNPUBLISHED_DATE")
            self.UNPUBLISHED_REASON_value = client.get_value_from_handle(
                pid, "EUDAT/UNPUBLISHED_REASON")

            log.info("""B2HANDLE response. URL: %s, EUDAT/CHECKSUM: %s,
                     EUDAT/UNPUBLISHED: %s, EUDAT/UNPUBLISHED_DATE: %s,
                     EUDAT/UNPUBLISHED_REASON: %s""",
                     self.URL_value, self.CHECKSUM_value,
                     self.UNPUBLISHED_value, self.UNPUBLISHED_DATE_value,
                     self.UNPUBLISHED_REASON_value)
        except handleexceptions.HandleSyntaxError as e:
            errorMessage = "B2HANDLE: %s" % str(e)
            log.warning(errorMessage)
            return self.send_errors(
                message=errorMessage, code=hcodes.HTTP_BAD_REQUEST)
        except handleexceptions.HandleNotFoundException as e:
            errorMessage = "B2HANDLE: %s" % str(e)
            log.critical(errorMessage)
            return self.send_errors(
                message=errorMessage, code=hcodes.HTTP_BAD_NOTFOUND)
        except handleexceptions.GenericHandleError as e:
            errorMessage = "B2HANDLE: %s" % str(e)
            log.warning(errorMessage)
        except handleexceptions.HandleAuthenticationError as e:
            errorMessage = "B2HANDLE: %s" % str(e)
            log.critical(errorMessage)
            return self.send_errors(
                message=errorMessage, code=hcodes.HTTP_BAD_UNAUTHORIZED)
