"""
B2SAFE HTTP REST API endpoints.
Getting informations for public data.
"""

import os

from b2stage.endpoints.commons.b2handle import B2HandleEndpoint
from b2stage.endpoints.commons.statics import FOOTER, HEADER
from restapi import decorators
from restapi.models import fields
from restapi.rest.response import ResponseMaker
from restapi.utilities.logs import log
from werkzeug.wrappers import Response as WerkzeugResponse


class Public(B2HandleEndpoint):

    labels = ["eudat", "pids", "public"]
    depends_on = ["IRODS_ANONYMOUS", "ENABLE_PUBLIC_ENDPOINT"]

    # "description": "Activate file downloading (if PID points to a single file)",
    @decorators.use_kwargs({"download": fields.Bool()}, locations=["query"])
    @decorators.endpoint(
        path="/public/<path:location>",
        summary="Let non-authenticated users get data about a public data-object",
        responses={200: "Informations about the data-object"},
    )
    def get(self, location, download=False):

        location = self.fix_location(location)

        ####################
        # check if public, with anonymous access in irods
        icom = self.get_service_instance(
            service_name="irods",
            user="anonymous",
            password="null",
            authscheme="credentials",
        )

        path = self.parse_path(location)
        is_collection = icom.is_collection(path)
        if is_collection:
            body = (
                "<h3> Failure </h3>"
                + "Path provided is a Collection.<br>"
                + "Listing is NOT yet implemented."
            )
            output = HEADER + body + FOOTER

            headers = {"Content-Type": "text/html; charset=utf-8"}
            return WerkzeugResponse(output, status=400, headers=headers)

        ####################
        # check if browser

        if "text/html" not in ResponseMaker.get_accepted_formats():
            # print("NOT HTML")
            return self.send_errors(
                "This endpoint is currently accessible only via Browser.", code=403,
            )

        if download:

            filename = os.path.basename(path)
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Disposition": f'attachment; filename="{filename}"',
            }
            return icom.read_in_streaming(path, headers=headers)

        md, _ = icom.get_metadata(path)

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
            for key, value in info.get("metadata", {}).items():
                if value is None:
                    continue
                metadata += "<tr>"
                metadata += "<th> <i>metadata</i> </th>"
                metadata += f"<th> {key.capitalize()} </th>"
                metadata += f"<td> {value} </td>"
                metadata += "</tr>\n"
            for key, value in md.items():
                if value is None:
                    continue
                metadata += "<tr>"
                metadata += "<th> <i>metadata</i> </th>"
                metadata += f"<th> {key.capitalize()} </th>"
                metadata += f"<td> {value} </td>"
                metadata += "</tr>\n"

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
                info.get("path"),
                info.get("link"),
            )

        ####################
        # print("HTML")
        output = HEADER + body + FOOTER

        headers = {"Content-Type": "text/html; charset=utf-8"}
        return WerkzeugResponse(output, headers=headers)
