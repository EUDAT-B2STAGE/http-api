# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
Getting informations for public data.
"""

from restapi.rest.response import WerkzeugResponse
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

        path, resource, _, force = \
            self.get_file_parameters(icom, path=location)
        is_collection = icom.is_collection(path)
        if is_collection:
            return self.send_errors(
                message="Path provided is a collection",
                code=hcodes.HTTP_BAD_REQUEST
            )

        ####################
        # check if browser
        from restapi.rest.response import get_accepted_formats, MIMETYPE_HTML
        accepted_formats = get_accepted_formats()
        if MIMETYPE_HTML not in accepted_formats:
            # print("NOT HTML")
            from utilities import htmlcodes as hcodes
            return self.send_errors(
                "This endpoint is currently accessible only via Browser.",
                code=hcodes.HTTP_BAD_FORBIDDEN,
            )

        if self.download_parameter():
            import os
            filename = os.path.basename(path)
            headers = {
                'Content-Type': 'application/octet-stream',
                'Content-Disposition': 'attachment; filename="%s"' % filename
            }
            return icom.read_in_streaming(path, headers=headers)

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

        title = "EUDAT: B2STAGE HTTP-API"
        header = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport"
      content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet"
    href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"
    integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm"
    crossorigin="anonymous">

    <link rel="stylesheet"
    href="https://v4-alpha.getbootstrap.com/examples/narrow-jumbotron/narrow-jumbotron.css">

    <title>%s</title>
</head>
<body>
 <div class="container">

      <div class="float-right">
        <table>
            <tr>
                <td>
                    <img
            src='https://www.eudat.eu/sites/default/files/logo-b2stage.png'
            width=75
            </td>
                <td>
                    <img
            src='https://www.eudat.eu/sites/default/files/EUDAT-logo.png'
            width=75
            </td>
            </tr>
        </table>

      </div>

      <div class="header clearfix">
        <h2 class="text-muted">
            EUDAT-B2STAGE: HTTP-API service
        </h2>
      </div>
""" % title

        footer = """

    <footer class="footer">
     <p>&copy; EUDAT 2018</p>
    </footer>

 </div>
</body>
</html>
"""

        metadata = ""
        try:
            _, info = jout.pop().popitem()
        except AttributeError:
            info = None
        except BaseException as e:
            info = None
            log.error("Unknown error: %s(%s)" % (e.__class__.__name__, e))
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

        if info is None:
            body = "<h3> Data Object not found </h3>"
        else:
            body = """
<h3> Data Object landing page </h3>

</br> </br>
Found a data object <b>publicy</b> available:
</br> </br>

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
        <td> <a href='%s?download=true' target='_blank'>link</a> </td>
    </tr>
</table>
</br> </br>

""" % (
                # info.get('dataobject'),
                metadata,
                info.get('path'),
                info.get('link'),
            )

        ####################
        # print("HTML")
        output = header + body + footer

        headers = {'Content-Type': 'text/html; charset=utf-8'}
        return WerkzeugResponse(output, headers=headers)
