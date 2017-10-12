# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.

Code to implement the extended endpoints

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/master/docs/user/endpoints.md

"""

import os
from restapi.flask_ext.flask_irods.client import IrodsException
from b2stage.apis.commons import CURRENT_HTTPAPI_SERVER
from b2stage.apis.commons.endpoint import EudatEndpoint

from restapi.services.uploader import Uploader
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate
from b2handle.handleclient import EUDATHandleClient as b2handle
from b2handle.clientcredentials import PIDClientCredentials as credentials
from b2handle import handleexceptions

from utilities.logs import get_logger

log = get_logger(__name__)


###############################
# Classes

class PIDEndpoint(Uploader, EudatEndpoint):

    """
    Handling PID requests.
    It includes some methods to connect to B2HANDLE.

    FIXME: it should become a dedicated service in rapydo.
    This way the client could be registered in memory with credentials
    only if the provided credentials are working.
    It should be read only access otherwise.

    """

    eudat_pid_fields = [
        "URL", "EUDAT/CHECKSUM", "EUDAT/UNPUBLISHED",
        "EUDAT/UNPUBLISHED_DATE", "EUDAT/UNPUBLISHED_REASON"
    ]

    def connect_client(self, force_no_credentials=False):

        found = False

        # With credentials
        if not force_no_credentials:
            file = os.environ.get('HANDLE_CREDENTIALS', None)
            if file is not None:
                from utilities import path
                credentials_path = path.build(file)
                found = path.file_exists_and_nonzero(credentials_path)
                if not found:
                    log.warning(
                        "B2HANDLE credentials file not found %s", file)

            if found:
                client = b2handle.instantiate_with_credentials(
                    credentials.load_from_JSON(file)
                )
                log.info("PID client connected: w/ credentials")
                return client, True

        client = b2handle.instantiate_for_read_access()
        log.warning("PID client connected: NO credentials")
        return client, False

    def handle_pid_fields(self, client, pid):
        """ Perform B2HANDLE request: retrieve URL from handle """

        data = {}
        try:
            for field in self.eudat_pid_fields:
                value = client.get_value_from_handle(pid, field)
                log.info("B2HANDLE: %s=%s", field, value)
                data[field] = value
        except handleexceptions.HandleSyntaxError as e:
            return data, e, hcodes.HTTP_BAD_REQUEST
        except handleexceptions.HandleNotFoundException as e:
            return data, e, hcodes.HTTP_BAD_NOTFOUND
        except handleexceptions.GenericHandleError as e:
            return data, e, hcodes.HTTP_SERVER_ERROR
        except handleexceptions.HandleAuthenticationError as e:
            return data, e, hcodes.HTTP_BAD_UNAUTHORIZED
        except BaseException as e:
            return data, e, hcodes.HTTP_SERVER_ERROR

        return data, None, hcodes.HTTP_FOUND

    def get_pid_metadata(self, pid):

        # First test: check if credentials exists and works
        client, authenticated = self.connect_client()
        data, error, code = self.handle_pid_fields(client, pid)

        # If credentials were found but they gave error
        # TODO: this should be tested at server startup!
        if error is not None and authenticated:
            log.error("B2HANDLE credentials problem: %s", error)
            client, _ = self.connect_client(force_no_credentials=True)
            data, error, code = self.handle_pid_fields(client, pid)

        # Still getting error? Raise any B2HANDLE library problem
        if error is not None:
            log.error("B2HANDLE problem: %s", error)
            return data, \
                self.send_errors(message='B2HANDLE: %s' % error, code=code)
        else:
            return data, None

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, pid=None):
        """ Get metadata or file from pid """

        if pid is None:
            return self.send_errors(
                message='Missing PID inside URI', code=hcodes.HTTP_BAD_REQUEST)

        # recover metadata from pid
        metadata, bad_response = self.get_pid_metadata(pid)
        if bad_response is not None:
            return bad_response
        url = metadata.get('URL')
        if url is None:
            return self.send_errors(
                message='B2HANDLE: empty URL_value returned',
                code=hcodes.HTTP_BAD_NOTFOUND)

        # parse query parameters
        self.get_input()
        download = False
        if (hasattr(self._args, 'download')):
            if self._args.download and 'true' in self._args.download.lower():
                download = True

        # If download is True, trigger file download
        if download:
            api_url = CURRENT_HTTPAPI_SERVER

            # If local HTTP-API perform a direct download
            # FIXME: the following code can be improved
            route = api_url + 'api/registered/'
            # route = route.replace('http://', '')

            if (url.startswith(route)):
                url = url.replace(route, '/')
                r = self.init_endpoint()
                if r.errors is not None:
                    return self.send_errors(errors=r.errors)
                url = self.download_object(r, url)
            else:
                # Perform a request to an external service?
                return self.send_warnings(
                    {'URL': url},
                    errors=[
                        "Data-object can't be downloaded by current " +
                        "HTTP-API server '%s'" % api_url
                    ]
                )
            return url

        # When no download is requested
        return metadata
