"""
Internal endpoints.
Code to implement the /api/internal endpoint

FIXME: TO BE DEPRECATED
"""

from b2stage.apis.commons import CURRENT_MAIN_ENDPOINT
from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi import decorators
from restapi.confs import TESTING
from restapi.models import fields
from restapi.services.authentication import Role

if TESTING:

    class MetadataEndpoint(EudatEndpoint):

        labels = ["helpers", "eudat"]

        @decorators.auth.require_all(Role.USER)
        @decorators.use_kwargs({"PID": fields.Str(required=True)})
        @decorators.endpoint(
            path="/metadata/<path:location>",
            summary="Add metadata to object",
            responses={200: "Metadata added"},
        )
        def patch(self, PID, location=None):
            """
            Add metadata to an object.
            """

            if location is None:
                return self.send_errors(
                    "Location: missing filepath inside URI", code=400
                )
            location = self.fix_location(location)

            ###################
            # BASIC INIT
            r = self.init_endpoint()
            if r.errors is not None:
                return self.send_errors(errors=r.errors)
            icom = r.icommands

            path = self.parse_path(location)

            icom.set_metadata(location, PID=PID)
            out, _ = icom.get_metadata(location)

            return {
                "metadata": out,
                "location": path,
                "link": self.httpapi_location(location, api_path=CURRENT_MAIN_ENDPOINT),
            }
