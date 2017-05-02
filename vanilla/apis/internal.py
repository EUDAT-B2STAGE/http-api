# -*- coding: utf-8 -*-

"""
Internal endpoints.

Code to implement the /api/internal endpoint

"""

import os
import irods
import time
import json
from flask import request, current_app

from eudat.apis.common import PRODUCTION
from eudat.apis.common.b2stage import EudatEndpoint

from flask_ext.flask_irods.client import IrodsException

from rapydo.utils import htmlcodes as hcodes
from rapydo import decorators as decorate
from rapydo.utils.logs import get_logger

log = get_logger(__name__)


###############################
# Classes

class MetadataEndpoint(EudatEndpoint):
    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def patch(self, irods_location=None):
        """
        Add metadata to an object.
        """

        if irods_location is None:
            return self.send_errors('Location: missing filepath inside URI',
                                    code=hcodes.HTTP_BAD_REQUEST)
        irods_location = self.fix_location(irods_location)

        ###################
        # BASIC INIT
        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors)
        icom = r.icommands
        
        path, resource, filename, force = \
            self.get_file_parameters(icom, path=irods_location)

        dct = {}
        pid = self._args.get('PID')
        if pid:
            dct['PID'] = pid

        checksum = self._args.get('EUDAT/CHECKSUM')
        if checksum:
            dct['EUDAT/CHECKSUM'] = checksum

        if dct:
            icom.set_metadata(irods_location, **dct)
            out, _ = icom.get_metadata(irods_location)

        return {
            'metadata' : out,
            'location': filename,
            'link': self.httpapi_location(irods_location)
        }