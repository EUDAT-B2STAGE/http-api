"""
Internal endpoints.
Code to implement the /api/internal endpoint

FIXME: TO BE DEPRECATED
"""

from b2stage.apis.commons import CURRENT_MAIN_ENDPOINT
from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi import decorators
from restapi.confs import TESTING
from restapi.connectors.irods.client import IrodsException

# from restapi.utilities.logs import log


if TESTING:

    class MetadataEndpoint(EudatEndpoint):

        labels = ["helpers", "eudat"]
        _PATCH = {
            "/metadata/<location>": {
                "summary": "Add metadata to object",
                "parameters": [
                    {
                        "name": "metadata",
                        "in": "body",
                        "required": True,
                        "schema": {"type": "array", "items": {"type": "string"}},
                    }
                ],
                "responses": {"200": {"description": "Metadata added"}},
            }
        }

        @decorators.catch_errors(exception=IrodsException)
        @decorators.auth.required(roles=["normal_user"])
        def patch(self, location=None):
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

            path, resource, filename, force = self.get_file_parameters(
                icom, path=location
            )

            dct = {}
            pid = self._args.get("PID")
            if pid:
                dct["PID"] = pid
            else:
                return self.send_errors("PID: missing parameter in JSON input")

            checksum = self._args.get("EUDAT/CHECKSUM")
            if checksum:
                dct["EUDAT/CHECKSUM"] = checksum

            out = None
            if dct:
                icom.set_metadata(location, **dct)
                out, _ = icom.get_metadata(location)

            return {
                "metadata": out,
                "location": filename,
                "link": self.httpapi_location(location, api_path=CURRENT_MAIN_ENDPOINT),
            }
