# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
Getting informations for public data.
"""

from werkzeug.wrappers import Response as WerkzeugResponse
from b2stage.apis.commons.b2handle import B2HandleEndpoint
from b2stage.apis.commons.statics import HEADER, FOOTER
from restapi import decorators
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class Public(B2HandleEndpoint):

    # schema_expose = True
    labels = ['eudat', 'pids', 'public']
    depends_on = ['IRODS_ANONYMOUS', 'ENABLE_PUBLIC_ENDPOINT']
    GET = {
        '/public/<location>': {
            'summary': 'Let non-authenticated users get data about a public data-object',
            'custom': {},
            'parameters': [
                {
                    'name': 'download',
                    'description': 'Activate file downloading (if PID points to a single file)',
                    'in': 'query',
                    'type': 'boolean',
                }
            ],
            'responses': {'200': {'description': 'Informations about the data-object'}},
        }
    }

    @decorators.catch_errors()
    def get(self, location):

        ####################
        # self.get_input()

        ####################
        if location is None:
            return self.send_errors(
                'Location: missing filepath inside URI', code=hcodes.HTTP_BAD_REQUEST
            )
        location = self.fix_location(location)

        ####################
        # check if public, with anonymous access in irods
        icom = self.get_service_instance(
            service_name='irods',
            user='anonymous',
            password='null',
            authscheme='credentials',
        )

        path, resource, _, force = self.get_file_parameters(icom, path=location)
        is_collection = icom.is_collection(path)
        if is_collection:
            body = (
                "<h3> Failure </h3>"
                + "Path provided is a Collection.<br>"
                + "Listing is NOT yet implemented."
            )
            output = HEADER + body + FOOTER

            headers = {'Content-Type': 'text/html; charset=utf-8'}
            return WerkzeugResponse(
                output, status=hcodes.HTTP_BAD_REQUEST, headers=headers
            )

        ####################
        # check if browser
        from restapi.rest.response import get_accepted_formats, MIMETYPE_HTML

        accepted_formats = get_accepted_formats()
        if MIMETYPE_HTML not in accepted_formats:
            # print("NOT HTML")
            return self.send_errors(
                "This endpoint is currently accessible only via Browser.",
                code=hcodes.HTTP_BAD_FORBIDDEN,
            )

        if self.download_parameter():
            import os

            filename = os.path.basename(path)
            headers = {
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': 'attachment; filename="{}"'.format(filename),
            }
            return icom.read_in_streaming(path, headers=headers)
        else:
            md, _ = icom.get_metadata(path)

        ####################
        # # look for pid metadata
        # pid = '11100/33ac01fc-6850-11e5-b66e-e41f13eb32b2'
        # metadata, bad_response = self.get_pid_metadata(pid)
        ####################
        # tmp = icom.list(location)

        # list content
        jout = self.list_objects(icom, path, is_collection, location, public=True)

        metadata = ""
        try:
            _, info = jout.pop().popitem()
        except AttributeError:
            info = None
        except BaseException as e:
            info = None
            log.error("Unknown error: {}({})", e.__class__.__name__, e)
        else:
            for key, value in info.get('metadata', {}).items():
                if value is None:
                    continue
                metadata += '<tr>'
                metadata += "<th> <i>metadata</i> </th>"
                metadata += "<th> {} </th>".format(key.capitalize())
                metadata += "<td> {} </td>".format(value)
                metadata += '</tr>\n'
            for key, value in md.items():
                if value is None:
                    continue
                metadata += '<tr>'
                metadata += "<th> <i>metadata</i> </th>"
                metadata += "<th> {} </th>".format(key.capitalize())
                metadata += "<td> {} </td>".format(value)
                metadata += '</tr>\n'

        if info is None:
            body = (
                "<h3> Failure </h3>"
                + "Data Object NOT found, or no permission to access.<br>"
            )
        else:
            body = """
<h3> Data Object landing page </h3>

</br> </br>
Found a data object <b>publicly</b> available:
</br> </br>

<table border=1 cellpadding=5 cellspacing=5>
    {}
    <tr>
        <th> <i>info</i> </th>
        <th> Collection </th>
        <td> {} </td>
    </tr>
    <tr>
        <th> <i>access</i> </th>
        <th> Download </th>
        <td> <a href='{}?download=true' target='_blank'>link</a> </td>
    </tr>
</table>
</br> </br>

""".format(
                # info.get('dataobject'),
                metadata,
                info.get('path'),
                info.get('link'),
            )

        ####################
        # print("HTML")
        output = HEADER + body + FOOTER

        headers = {'Content-Type': 'text/html; charset=utf-8'}
        return WerkzeugResponse(output, headers=headers)
