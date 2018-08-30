# -*- coding: utf-8 -*-

"""
Internal endpoints.
Code to implement the /api/internal endpoint

FIXME: TO BE DEPRECATED
"""

from b2stage.apis.commons.endpoint import EudatEndpoint
from b2stage.apis.commons import CURRENT_MAIN_ENDPOINT
from restapi import decorators as decorate
from restapi.flask_ext.flask_irods.client import IrodsException
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


###############################
# Classes

class MetadataEndpoint(EudatEndpoint):
    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def patch(self, location=None):
        """
        Add metadata to an object.
        """

        if location is None:
            return self.send_errors('Location: missing filepath inside URI',
                                    code=hcodes.HTTP_BAD_REQUEST)
        location = self.fix_location(location)

        ###################
        # BASIC INIT
        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors)
        icom = r.icommands

        path, resource, filename, force = \
            self.get_file_parameters(icom, path=location)

        dct = {}
        pid = self._args.get('PID')
        if pid:
            dct['PID'] = pid
        else:
            return self.send_errors('PID: missing parameter in JSON input')

        checksum = self._args.get('EUDAT/CHECKSUM')
        if checksum:
            dct['EUDAT/CHECKSUM'] = checksum

        out = None
        if dct:
            icom.set_metadata(location, **dct)
            out, _ = icom.get_metadata(location)

        return {
            'metadata': out,
            'location': filename,
            'link': self.httpapi_location(
                location, api_path=CURRENT_MAIN_ENDPOINT
            )
        }
