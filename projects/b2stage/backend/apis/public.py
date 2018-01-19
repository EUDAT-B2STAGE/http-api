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
        is_collection = icom.is_collection(path)
        if is_collection:
            return self.send_errors(
                message="Path provided is a collection",
                code=hcodes.HTTP_BAD_REQUEST
            )

        if self.download_parameter():
            return "To be downloaded!!!"

        ####################
        # # look for pid metadata
        # pid = '11100/33ac01fc-6850-11e5-b66e-e41f13eb32b2'
        # metadata, bad_response = self.get_pid_metadata(pid)
        ####################
        # tmp = icom.list(location)
        # log.pp(tmp)

        # list content
        jout = self.list_objects(icom,
                                 path, is_collection, location, public=True)

        # ####################
        # # check if browser
        # from restapi.rest.response import request_from_browser
        # if not request_from_browser:
        #     return 'Not a browser'

        from restapi.rest.response import get_accepted_formats, MIMETYPE_HTML
        accepted_formats = get_accepted_formats()
        if MIMETYPE_HTML in accepted_formats:

            title = "EUDAT: B2STAGE HTTP-API"
            header = """<!DOCTYPE html>
<html>
<head> <title>%s</title> </head>
<body>
""" % title

            footer = """
</body>
</html>
"""

            # body = "<p><b>Test</b></p>\n"
            body = """

<table>
    <tr>
        <td>
            <img
    src='https://www.eudat.eu/sites/default/files/logo-b2stage.png'
    width=150
    </td>
        <td>
            <img
    src='https://www.eudat.eu/sites/default/files/EUDAT-logo.png'
    width=150
    </td>
    </tr>
</table>
"""

            metadata = ""
            try:
                _, info = jout.pop().popitem()
            except IndexError:
                # NOTE: probably some error if here, to catch?
                info = {}
            else:
                # log.pp(info)
                for key, value in info.get('metadata', {}).items():
                    if value is None:
                        continue
                    metadata += '<tr>'
                    metadata += "<th> <i>metadata</i> </th>"
                    metadata += "<th> %s </th>" % key.capitalize()
                    metadata += "<td> %s </td>" % value
                    metadata += '</tr>\n'

            body += """
<table border=1 cellpadding=5 cellspacing=5>
    %s
    <tr>
        <th> <i>info</i> </th>
        <th> Collection </th>
        <td> %s </td>
    </tr>
    <tr>
        <th> <i>access</i> </th>
        <th> Download </th>
        <td> <a href='%s?download=true'>link</a> </td>
    </tr>
</table>

""" % (
                # info.get('dataobject'),
                metadata,
                info.get('path'),
                info.get('link'),
            )

            ####################
            # print("HTML")
            output = header + body + footer

            from restapi.rest.response import WerkzeugResponse
            headers = {'Content-Type': 'text/html; charset=utf-8'}
            return WerkzeugResponse(output, headers=headers)
            # return respond_to_browser(r)

        else:  # if MIMETYPE_JSON in accepted_formats:
            # print("NOT HTML")
            output = jout

        return output
