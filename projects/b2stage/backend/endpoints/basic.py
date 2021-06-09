"""
B2SAFE HTTP REST API endpoints.

Code to implement the /api/resources endpoint

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/metadata_parser/docs/user/endpoints.md

"""

import os
import time
from pathlib import Path

from b2stage.connectors.irods.client import IrodsException
from b2stage.endpoints.commons import CURRENT_MAIN_ENDPOINT
from b2stage.endpoints.commons.endpoint import EudatEndpoint
from flask import request
from restapi import decorators
from restapi.config import TESTING
from restapi.exceptions import RestApiException
from restapi.models import fields
from restapi.services.authentication import Role
from restapi.services.uploader import Uploader
from restapi.utilities.logs import log

###############################
# Classes


class BasicEndpoint(Uploader, EudatEndpoint):

    labels = ["eudat", "registered"]

    @decorators.auth.require_all(Role.USER)
    # "description": "activate file downloading (if path is a single file)",
    @decorators.use_kwargs({"download": fields.Bool()}, location="query")
    @decorators.endpoint(
        path="/registered/<path:location>",
        summary="Retrieve digital object information or download it",
        responses={
            200: "Returns the digital object information or file content if download is activated or the list of objects related to the requested path (pid is returned if available)"
        },
    )
    def get(self, location, download=False):
        """Download file from filename"""

        location = self.fix_location(location)

        ###################
        # Init EUDAT endpoint resources
        r = self.init_endpoint()
        if r.errors is not None:
            raise RestApiException(r.errors)

        # get parameters with defaults
        icom = r.icommands
        path = self.parse_path(location)

        is_collection = icom.is_collection(path)
        # Check if it's not a collection because the object does not exist
        # do I need this??
        # if not is_collection:
        #     icom.get_dataobject(path)

        ###################
        # DOWNLOAD a specific file
        ###################

        # If download is True, trigger file download
        if download:
            if is_collection:
                raise RestApiException("Collection: recursive download is not allowed")
            # NOTE: we always send in chunks when downloading
            return icom.read_in_streaming(path)

        return self.list_objects(icom, path, is_collection, location)

    @decorators.auth.require_all(Role.USER)
    @decorators.use_kwargs({"force": fields.Bool(), "path": fields.Str(required=True)})
    @decorators.endpoint(
        path="/registered",
        summary="Create a new collection",
        responses={200: "Collection created"},
    )
    def post(self, path, force=False):
        """
        Handle [directory creation](docs/user/registered.md#post).
        Test on internal client shell with:
        http --form POST \
            $SERVER/api/resources?path=/tempZone/home/guest/test \
            force=True "$AUTH"
        """

        # Disable upload for POST method
        if "file" in request.files:
            raise RestApiException(
                "File upload forbidden for this method; "
                "Please use the PUT method for this operation",
                status_code=405,
            )

        ###################
        # BASIC INIT
        r = self.init_endpoint()
        if r.errors is not None:
            raise RestApiException(r.errors)

        icom = r.icommands
        # get parameters with defaults
        path = self.parse_path(path)

        # if path variable empty something is wrong
        if path is None:
            raise RestApiException(
                "Path to remote resource: only absolute paths are allowed",
                status_code=405,
            )

        ###################
        # Create Directory

        ipath = icom.create_directory(path, ignore_existing=force)
        if ipath is None:
            if not force:
                raise IrodsException(f"Failed to create {path}")
            ipath = path
        else:
            log.info("Created irods collection: {}", ipath)

        # NOTE: question: should this status be No response?
        status = 200
        content = {
            "location": self.b2safe_location(path),
            "path": path,
            "link": self.httpapi_location(path, api_path=CURRENT_MAIN_ENDPOINT),
        }

        return self.response(content, code=status)

    @decorators.auth.require_all(Role.USER)
    @decorators.use_kwargs(
        {"resource": fields.Str(), "force": fields.Bool(), "pid_await": fields.Bool()}
    )
    @decorators.endpoint(
        path="/registered/<path:location>",
        summary="Upload a new file",
        responses={200: "File created"},
    )
    def put(self, location, resource=None, force=False, pid_await=False):
        """
        Handle file upload. Test on docker client shell with:
        http --form PUT $SERVER/api/resources/tempZone/home/guest/test \
            file@SOMEFILE force=True "$AUTH"
        Note to devs: iRODS does not allow to iput on more than one resource.
        To put the second one you need the irepl command,
        which will assure that we have a replica on all resources...

        NB: to be able to read "request.stream", request should not be already
        be conusmed before (for instance with request.data or request.get_json)

        To stream upload with CURL:
        curl -v -X PUT --data-binary "@filename" \
          apiserver.dockerized.io:5000/api/registered/tempZone/home/guest  \
          -H "$AUTH" -H "Content-Type: application/octet-stream"
        curl -T filename \
            apiserver.dockerized.io:5000/api/registered/tempZone/home/guest \
            -H "$AUTH" -H "Content-Type: application/octet-stream"

        To stream upload with python requests:
        import requests

        headers = {
            "Authorization":"Bearer <token>",
            "Content-Type":"application/octet-stream"
        }

        with open('/tmp/filename', 'rb') as f:
            requests.put(
                'http://localhost:8080/api/registered' +
                '/tempZone/home/guest/prova', data=f, headers=headers)
        """

        location = self.fix_location(location)
        # NOTE: location will act strange due to Flask internals
        # in case upload is served with streaming options,
        # NOT finding the right path + filename if the path is a collection

        ###################
        # Basic init
        r = self.init_endpoint()
        if r.errors is not None:
            raise RestApiException(r.errors)

        icom = r.icommands
        # get parameters with defaults
        """
        NOTE: resource is a complicated parameter:
        resources are meant for (iRODS) replicas;
        adding or removing replicas require explicit irods commands.
        """

        path = self.parse_path(location)

        # Manage both form and streaming upload
        ipath = None
        filename = None

        #################
        # CASE 1- FORM UPLOAD
        if request.mimetype != "application/octet-stream":

            # Normal upload: inside the host tmp folder
            try:
                username_path = Path(r.username)
                errors = None
                status = 200

                # DEBUG CODE
                log.critical(
                    "DEBUG CODE: /uploads permssions = {}",
                    oct(os.stat(Path("/uploads")).st_mode & 0o777),
                )

                # ################
                response = self.upload(subfolder=username_path, force=force)
                content = response[0]
                original_filename = content.get("filename")
                abs_file = self.absolute_upload_file(original_filename, username_path)
                log.info("File is '{}'", abs_file)

                # Move file in irods
                # Verify if the current path proposed from the user
                # is indeed an existing collection in iRODS
                if icom.is_collection(path):
                    # When should the original name be used?
                    # Only if the path specified is an
                    # existing irods collection
                    filename = original_filename
                else:
                    filename = None

                try:
                    # Handling (iRODS) path
                    ipath = self.complete_path(path, filename)
                    log.debug("Save into: {}", ipath)
                    iout = icom.save(
                        abs_file, destination=ipath, force=force, resource=resource
                    )
                    log.info("irods call {}", iout)
                finally:
                    # Transaction rollback: remove local cache in any case
                    log.debug("Removing cache object")
                    os.remove(abs_file)

            except RestApiException as e:

                content = None
                errors = str(e)
                status = e.status_code

        #################
        # CASE 2 - STREAMING UPLOAD
        else:
            filename = None

            try:
                # Handling (iRODS) path
                ipath = self.complete_path(path, filename)
                iout = icom.write_in_streaming(
                    destination=ipath, force=force, resource=resource
                )
                log.info("irods call {}", iout)
                content = {"filename": ipath}
                errors = None
                status = 200
            except BaseException as e:
                content = ""
                errors = {"Uploading failed": f"{e}"}
                status = 500

        ###################
        # Reply to user
        if filename is None:
            filename = self.filename_from_path(path)

        pid_found = True
        if not errors:
            out = {}
            if pid_await:
                # Shall we get the timeout from user?
                pid_found = False
                timeout = time.time() + 10  # seconds from now
                pid = ""
                while True:
                    out, _ = icom.get_metadata(ipath)
                    pid = out.get("PID")
                    if pid is not None or time.time() > timeout:
                        break
                    time.sleep(2)
                if not pid:
                    error_message = (
                        "Timeout waiting for PID from B2SAFE:"
                        " the object registration may be still in progress."
                        " File correctly uploaded."
                    )
                    log.warning(error_message)
                    status = 202
                    errors = error_message
                else:
                    pid_found = True

            # Get iRODS checksum
            obj = icom.get_dataobject(ipath)
            checksum = obj.checksum

            content = {
                "location": self.b2safe_location(ipath),
                "PID": out.get("PID"),
                "checksum": checksum,
                "filename": filename,
                "path": path,
                "link": self.httpapi_location(
                    ipath, api_path=CURRENT_MAIN_ENDPOINT, remove_suffix=path
                ),
            }

        if errors:
            raise RestApiException(errors, status_code=status)

        if not pid_found:
            status = 202

        return self.response(content, code=status)

    @decorators.auth.require_all(Role.USER)
    @decorators.use_kwargs({"newname": fields.Str(required=True)})
    @decorators.endpoint(
        path="/registered/<path:location>",
        summary="Update an entity name",
        responses={200: "File name updated"},
    )
    def patch(self, location, newname):
        """
        PATCH a record. E.g. change only the filename to a resource.
        """

        location = self.fix_location(location)

        ###################
        # BASIC INIT
        r = self.init_endpoint()
        if r.errors is not None:
            raise RestApiException(r.errors)

        icom = r.icommands

        # Get the base directory
        collection = icom.get_collection_from_path(location)
        # Set the new absolute path
        newpath = icom.get_absolute_path(newname, root=collection)
        # Move in irods
        icom.move(location, newpath)

        return {
            "location": self.b2safe_location(newpath),
            "filename": newname,
            "path": collection,
            "link": self.httpapi_location(
                newpath, api_path=CURRENT_MAIN_ENDPOINT, remove_suffix=location
            ),
        }

    @decorators.auth.require_all(Role.USER)
    @decorators.endpoint(
        path="/registered/<path:location>",
        summary="Delete an entity",
        responses={200: "Entity deleted"},
    )
    def delete(self, location):
        """
        Remove an object or an empty directory on iRODS

        http DELETE \
            $SERVER/api/resources/tempZone/home/guest/test/filename "$AUTH"
        """

        ###################
        # BASIC INIT

        # get the base objects
        r = self.init_endpoint()
        if r.errors is not None:
            raise RestApiException(r.errors)

        # icom = r.icommands

        # TODO: only if it has a PID?
        raise RestApiException(
            "Data removal NOT allowed inside the 'registered' domain",
            status_code=405,
        )


if TESTING:

    class DeleteAllTestingMode(Uploader, EudatEndpoint):

        labels = ["eudat", "registered"]

        @decorators.auth.require_all(Role.USER)
        @decorators.endpoint(
            path="/testdeleteall",
            summary="Delete an entity",
            responses={200: "Entities deleted"},
        )
        def delete(self):
            """
            Cleanup a home collection, only enabled in TESTING mode
            """

            # get the base objects
            r = self.init_endpoint()
            if r.errors is not None:
                raise RestApiException(r.errors)

            icom = r.icommands

            home = icom.get_user_home()
            files = icom.list(home)
            for key, obj in files.items():
                icom.remove(
                    home + self._path_separator + obj["name"],
                    recursive=obj["object_type"] == "collection",
                )
                log.debug("Removed {}", obj["name"])
            return self.response("Cleaned")
