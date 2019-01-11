# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
Code to implement the extended endpoints.

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/master/docs/user/endpoints.md

"""

from restapi.flask_ext.flask_irods.client import IrodsException
from b2stage.apis.commons.b2handle import B2HandleEndpoint

from restapi.services.uploader import Uploader
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate

from utilities.logs import get_logger

log = get_logger(__name__)


class PIDEndpoint(Uploader, B2HandleEndpoint):
    """ Handling PID on endpoint requests """

    def eudat_pid(self, pid):

        # recover metadata from pid
        metadata, bad_response = self.get_pid_metadata(pid)
        if bad_response is not None:
            return bad_response
        url = metadata.get('URL')
        if url is None:
            return self.send_errors(
                message='B2HANDLE: empty URL_value returned',
                code=hcodes.HTTP_BAD_NOTFOUND)

        if not self.download_parameter():
            return metadata

        # download is requested, trigger file download

        from b2stage.apis.commons import \
            CURRENT_HTTPAPI_SERVER, CURRENT_MAIN_ENDPOINT, PUBLIC_ENDPOINT
        rroute = '%s/%s/' % (CURRENT_HTTPAPI_SERVER, CURRENT_MAIN_ENDPOINT)
        proute = '%s/%s/' % (CURRENT_HTTPAPI_SERVER, PUBLIC_ENDPOINT)
        # route = route.replace('http://', '')

        url = url.replace('https://', '')
        url = url.replace('http://', '')

        log.warning(rroute)
        log.warning(proute)

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
                ]
            )

        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors)
        url = self.download_object(r, url)
        return url

    def seadata_pid(self, pid):

        response = {
            'PID': pid,
            'verified': False,
            'metadata': {},
        }

        #################
        # b2handle to verify PID
        b2handle_output = self.check_pid_content(pid)
        if b2handle_output is None:
            error = {'B2HANDLE': 'not found'}
            log.error(error)
            return self.send_warnings(
                response,
                errors=error, code=hcodes.HTTP_BAD_REQUEST)
        else:
            log.verbose("PID %s verified", pid)
            response['verified'] = True
            log.pp(b2handle_output)

        #################
        ipath = self.parse_pid_dataobject_path(b2handle_output)
        from utilities import path
        response['temp_id'] = path.last_part(ipath)
        response['batch_id'] = path.last_part(path.dir_name(ipath))

        #################
        # get the metadata
        # imain = self.get_service_instance(service_name='irods')
        imain = self.get_main_irods_connection()
        metadata, _ = imain.get_metadata(ipath)
        log.pp(metadata)

        from b2stage.apis.commons.seadatacloud import Metadata as md
        for key, value in metadata.items():
            if key in md.keys:
                response['metadata'][key] = value

        return response

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, pid):
        """ Get metadata or file from pid """

        # if pid is None:
        #     return self.send_errors(
        #         message='Missing PID inside URI',
        #         code=hcodes.HTTP_BAD_REQUEST)

        from b2stage.apis.commons.seadatacloud import SEADATA_ENABLED
        if SEADATA_ENABLED:
            return self.seadata_pid(pid)
        else:
            return self.eudat_pid(pid)
