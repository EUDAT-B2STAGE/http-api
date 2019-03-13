# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
Code to implement the extended endpoints.

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/master/docs/user/endpoints.md

"""

from restapi.flask_ext.flask_irods.client import IrodsException
from restapi.exceptions import RestApiException
from b2stage.apis.commons.b2handle import B2HandleEndpoint
from b2stage.apis.commons import CURRENT_HTTPAPI_SERVER, CURRENT_MAIN_ENDPOINT
from b2stage.apis.commons import PUBLIC_ENDPOINT

from restapi.services.uploader import Uploader
from restapi.services.download import Downloader
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate

from utilities.logs import get_logger

log = get_logger(__name__)


class PIDEndpoint(Uploader, Downloader, B2HandleEndpoint):
    """ Handling PID on endpoint requests """

    def eudat_pid(self, pid, head=False):

        # recover metadata from pid
        metadata, bad_response = self.get_pid_metadata(pid, head_method=head)
        if bad_response is not None:
            return bad_response
        url = metadata.get('URL')
        if url is None:
            return self.send_errors(
                message='B2HANDLE: empty URL_value returned',
                code=hcodes.HTTP_BAD_NOTFOUND,
                head_method=head
            )

        if not self.download_parameter():
            if head:
                return self.force_response("", code=hcodes.HTTP_OK_BASIC)
            return metadata
        # download is requested, trigger file download

        rroute = '%s%s/' % (CURRENT_HTTPAPI_SERVER, CURRENT_MAIN_ENDPOINT)
        proute = '%s%s/' % (CURRENT_HTTPAPI_SERVER, PUBLIC_ENDPOINT)
        # route = route.replace('http://', '')

        url = url.replace('https://', '')
        url = url.replace('http://', '')

        # If local HTTP-API perform a direct download
        if url.startswith(rroute):
            url = url.replace(rroute, '/')
        elif url.startswith(proute):
            url = url.replace(proute, '/')
        else:
            # Otherwise, perform a request to an external service?
            return self.send_warnings(
                {'URL': url},
                errors=[
                    "Data-object can't be downloaded by current " +
                    "HTTP-API server '%s'" % CURRENT_HTTPAPI_SERVER
                ],
                head_method=head
            )

        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors, head_method=head)
        url = self.download_object(r, url)

        if head:
            return self.force_response("", code=hcodes.HTTP_OK_BASIC)

        return url

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, pid):
        """ Get metadata or file from pid """

        try:
            from seadata.apis.commons.seadatacloud import seadata_pid
            return seadata_pid(self, pid)
        except ImportError:
            return self.eudat_pid(pid, head=False)

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def head(self, pid):
        """ Get metadata or file from pid """

        return self.eudat_pid(pid, head=True)
