# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
Getting informations for public data.
"""

from b2stage.apis.commons.b2handle import B2HandleEndpoint
from restapi import decorators as decorate
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


class Public(B2HandleEndpoint):

    @decorate.catch_error()
    def get(self, location):

        ####################
        # self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')

        ####################
        if location is None:
            return self.send_errors(
                'Location: missing filepath inside URI',
                code=hcodes.HTTP_BAD_REQUEST)
        location = self.fix_location(location)

        ####################
        # check if public, with anonymous access in irods
        icom = self.get_service_instance(
            service_name='irods', user='anonymous', password='null')

        path, resource, filename, force = \
            self.get_file_parameters(icom, path=location)
        if icom.is_collection(path):
            return self.send_errors(
                message="Path provided is a collection",
                code=hcodes.HTTP_BAD_REQUEST
            )

        # list content
        tmp = icom.list(location)
        log.pp(tmp)

        ####################
        # # look for pid metadata
        # pid = '11100/33ac01fc-6850-11e5-b66e-e41f13eb32b2'
        # metadata, bad_response = self.get_pid_metadata(pid)

        ####################
        # check if browser
        from restapi.rest.response import request_from_browser
        if request_from_browser:
            # # use logos in an html reply
            # https://www.eudat.eu/sites/default/files/logo-b2stage.png
            # https://www.eudat.eu/sites/default/files/EUDAT-logo.png
            return """ </br> <p> This is <b>HTML</b> content </p> """

        ####################
        return 'Not a browser'
