"""
B2SAFE HTTP REST API endpoints.
Code to implement the extended endpoints.

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/master/docs/user/endpoints.md

"""

from b2stage.endpoints.commons import (
    CURRENT_HTTPAPI_SERVER,
    CURRENT_MAIN_ENDPOINT,
    PUBLIC_ENDPOINT,
)
from b2stage.endpoints.commons.b2handle import B2HandleEndpoint
from restapi import decorators
from restapi.models import fields
from restapi.services.authentication import Role
from restapi.services.download import Downloader
from restapi.services.uploader import Uploader


class PIDEndpoint(Uploader, Downloader, B2HandleEndpoint):
    """ Handling PID on endpoint requests """

    labels = ["eudat", "pids"]

    def eudat_pid(self, pid, download, head=False):

        # recover metadata from pid
        metadata = self.get_pid_metadata(pid, head_method=head)
        url = metadata.get("URL")
        if url is None:
            return self.send_errors(
                errors="B2HANDLE: empty URL_value returned", code=404, head_method=head,
            )

        if not download and head:
            return self.response("", code=200)
        if not download:
            return metadata
        # download is requested, trigger file download

        rroute = f"{CURRENT_HTTPAPI_SERVER}{CURRENT_MAIN_ENDPOINT}/"
        proute = f"{CURRENT_HTTPAPI_SERVER}{PUBLIC_ENDPOINT}/"
        # route = route.replace('http://', '')

        url = url.replace("https://", "")
        url = url.replace("http://", "")

        # If local HTTP-API perform a direct download
        if url.startswith(rroute):
            url = url.replace(rroute, "/")
        elif url.startswith(proute):
            url = url.replace(proute, "/")
        else:
            # Otherwise, perform a request to an external service?
            return self.response(
                {"URL": url},
                errors=[
                    "Data-object can't be downloaded by current "
                    + f"HTTP-API server '{CURRENT_HTTPAPI_SERVER}'"
                ],
                head_method=head,
            )
        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors, head_method=head)

        return self.download_object(r, url, head=head)

    @decorators.auth.require_all(Role.USER)
    # "description": "Activate file downloading (if PID points to a single file)",
    @decorators.use_kwargs({"download": fields.Bool()}, location="query")
    @decorators.endpoint(
        path="/pids/<path:pid>",
        summary="Resolve a pid and retrieve metadata or download it link object",
        responses={
            200: "The information related to the file which the pid points to or the file content if download is activated or the list of objects if the pid points to a collection"
        },
    )
    def get(self, pid, download=False):
        """ Get metadata or file from pid """

        try:
            from seadata.endpoints.commons.seadatacloud import seadata_pid

            return seadata_pid(self, pid)
        except ImportError:
            return self.eudat_pid(pid, download, head=False)

    # "description": "Activate file downloading (if PID points to a single file)",
    @decorators.auth.require_all(Role.USER)
    @decorators.use_kwargs({"download": fields.Bool()}, location="query")
    @decorators.endpoint(
        path="/pids/<path:pid>",
        summary="Resolve a pid and verify permission of the digital object",
        responses={
            200: "The pid can be resolved and the digital object can be downloaded (if download parameter is provided)"
        },
    )
    def head(self, pid, download=False):
        """ Get metadata or file from pid """

        return self.eudat_pid(pid, download, head=True)
