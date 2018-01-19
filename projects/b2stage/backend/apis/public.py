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

        ####################
        # # look for pid metadata
        # pid = '11100/33ac01fc-6850-11e5-b66e-e41f13eb32b2'
        # metadata, bad_response = self.get_pid_metadata(pid)
        ####################
        # tmp = icom.list(location)
        # log.pp(tmp)

        # list content
        is_collection = icom.is_collection(path)
        jout = self.list_objects(icom, path, is_collection, location)

        # ####################
        # # check if browser
        # from restapi.rest.response import request_from_browser
        # if not request_from_browser:
        #     return 'Not a browser'

        from restapi.rest.response import get_accepted_formats, MIMETYPE_HTML
        accepted_formats = get_accepted_formats()
        if MIMETYPE_HTML in accepted_formats:

            ####################
            # # use logos in an html reply
            # https://www.eudat.eu/sites/default/files/logo-b2stage.png
            # https://www.eudat.eu/sites/default/files/EUDAT-logo.png

            # print("HTML")
            output = """ </br> <p> This is <b>HTML</b> content! </p>
                <pre>%s</pre>""" % jout
            from restapi.rest.response import WerkzeugResponse
            headers = {'Content-Type': 'text/html; charset=utf-8'}
            return WerkzeugResponse(output, headers=headers)
            # return respond_to_browser(r)

        else:  # if MIMETYPE_JSON in accepted_formats:
            # print("NOT HTML")
            output = jout

        return output
