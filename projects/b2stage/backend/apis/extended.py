# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
Code to implement the extended endpoints.

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/master/docs/user/endpoints.md

"""

from restapi.flask_ext.flask_irods.client import IrodsException
from b2stage.apis.commons import CURRENT_HTTPAPI_SERVER
from b2stage.apis.commons.b2handle import B2HandleEndpoint

from restapi.services.uploader import Uploader
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate

from utilities.logs import get_logger

log = get_logger(__name__)


class PIDEndpoint(Uploader, B2HandleEndpoint):
    """ Handling PID on endpoint requests """

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
