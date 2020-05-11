# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.

Code to implement the /api/resources endpoint

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/metadata_parser/docs/user/endpoints.md

"""

import os
import time
import json
from glom import glom
from flask import request

from restapi.confs import TESTING
from b2stage.apis.commons import PRODUCTION, CURRENT_MAIN_ENDPOINT
from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi import decorators
from restapi.services.uploader import Uploader
from restapi.exceptions import RestApiException
from restapi.connectors.irods.client import IrodsException
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


###############################
# Classes


class BasicEndpoint(Uploader, EudatEndpoint):

    labels = ['eudat', 'registered']
    GET = {
        '/registered/<path:location>': {
            'custom': {},
            'summary': 'Retrieve a single digital entity/object information or download it',
            'parameters': [
                {
                    'name': 'download',
                    'description': 'activate file downloading (if path is a single file)',
                    'in': 'query',
                    'type': 'boolean',
                }
            ],
            'responses': {
                '200': {
                    'description': 'Returns the digital object information or file content if download is activated or the list of objects related to the requested path (PID is returned if available)'
                }
            },
        }
    }
    POST = {
        '/registered': {
            'summary': 'Create a new collection',
            'custom': {},
            'responses': {'200': {'description': 'Collection created'}},
            'parameters': [
                {
                    'name': 'path',
                    'in': 'query',
                    'type': 'string',
                    'description': 'the filesystem path to created collection',
                }
            ],
        }
    }
    PUT = {
        '/registered/<path:location>': {
            'summary': 'Upload a new file',
            'custom': {},
            'responses': {'200': {'description': 'File created'}},
            'parameters': [
                {
                    'name': 'file',
                    'in': 'formData',
                    'description': 'file data to be uploaded',
                    'required': True,
                    'type': 'file',
                },
                {
                    'name': 'force',
                    'in': 'query',
                    'type': 'boolean',
                    'description': 'force action even if getting warnings',
                },
                {
                    'name': 'pid_await',
                    'in': 'query',
                    'type': 'boolean',
                    'description': 'Returns PID in the JSON response',
                },
            ],
        }
    }
    PATCH = {
        '/registered/<path:location>': {
            'summary': 'Update an entity name',
            'custom': {},
            'parameters': [
                {
                    'name': 'new file name',
                    'in': 'body',
                    'schema': {'$ref': '#/definitions/FileUpdate'},
                }
            ],
            'responses': {'200': {'description': 'File name updated'}},
        }
    }
    DELETE = {
        '/registered': {
            'custom': {},
            'summary': 'Delete an entity',
            'parameters': [
                {
                    'name': 'debugclean',
                    'in': 'query',
                    'type': 'boolean',
                    'description': 'Only for debug mode',
                }
            ],
            'responses': {'200': {'description': 'Entities deleted'}},
        },
        '/registered/<path:location>': {
            'custom': {},
            'summary': 'Delete an entity',
            'parameters': [
                {
                    'name': 'debugclean',
                    'in': 'query',
                    'type': 'boolean',
                    'description': 'Only for debug mode',
                }
            ],
            'responses': {'200': {'description': 'Entity deleted'}},
        },
    }

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required(roles=['normal_user'])
    def get(self, location):
        """ Download file from filename """

        location = self.fix_location(location)

        ###################
        # Init EUDAT endpoint resources
        r = self.init_endpoint()
        if r.errors is not None:
            raise RestApiException(r.errors)

        # get parameters with defaults
        icom = r.icommands
        path, resource, filename, force = self.get_file_parameters(icom, path=location)

        is_collection = icom.is_collection(path)
        # Check if it's not a collection because the object does not exist
        # do I need this??
        # if not is_collection:
        #     icom.get_dataobject(path)

        ###################
        # DOWNLOAD a specific file
        ###################

        # If download is True, trigger file download
        if hasattr(self._args, 'download'):
            if self._args.download and 'true' in self._args.download.lower():
                if is_collection:
                    raise RestApiException(
                        'Collection: recursive download is not allowed'
                    )
                else:
                    # NOTE: we always send in chunks when downloading
                    return icom.read_in_streaming(path)

        return self.list_objects(icom, path, is_collection, location)

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required(roles=['normal_user'])
    def post(self):
        """
        Handle [directory creation](docs/user/registered.md#post).
        Test on internal client shell with:
        http --form POST \
            $SERVER/api/resources?path=/tempZone/home/guest/test \
            force=True "$AUTH"
        """

        # Disable upload for POST method
        if 'file' in request.files:
            raise RestApiException(
                'File upload forbidden for this method; '
                'Please use the PUT method for this operation',
                status_code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED,
            )

        ###################
        # BASIC INIT
        r = self.init_endpoint()
        if r.errors is not None:
            raise RestApiException(r.errors)

        icom = r.icommands
        # get parameters with defaults
        path, resource, filename, force = self.get_file_parameters(icom)

        # if path variable empty something is wrong
        if path is None:
            raise RestApiException(
                'Path to remote resource: only absolute paths are allowed',
                status_code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED,
            )

        ###################
        # Create Directory

        ipath = icom.create_directory(path, ignore_existing=force)
        if ipath is None:
            if force:
                ipath = path
            else:
                raise IrodsException("Failed to create {}".format(path))
        else:
            log.info("Created irods collection: {}", ipath)

        # NOTE: question: should this status be No response?
        status = hcodes.HTTP_OK_BASIC
        content = {
            'location': self.b2safe_location(path),
            'path': path,
            'link': self.httpapi_location(path, api_path=CURRENT_MAIN_ENDPOINT),
        }

        return self.response(content, code=status)

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required(roles=['normal_user'])
    def put(self, location):
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
        path, resource, filename, force = self.get_file_parameters(icom, path=location)

        # Manage both form and streaming upload
        ipath = None

        #################
        # CASE 1- FORM UPLOAD
        if request.mimetype != 'application/octet-stream':

            # Read the request
            request.get_data()

            # Normal upload: inside the host tmp folder
            try:
                response = self.upload(subfolder=r.username, force=force)
                content = json.loads(response.get_data().decode())
                # This is required for wrapped response, remove me in a near future
                content = glom(content, "Response.data", default=content)
                errors = None
                status = hcodes.HTTP_OK_BASIC

            except RestApiException as e:

                content = None
                errors = str(e)
                status = e.status_code

            ###################
            # If files uploaded
            key_file = 'filename'

            if isinstance(content, dict) and key_file in content:
                original_filename = content[key_file]
                abs_file = self.absolute_upload_file(original_filename, r.username)
                log.info("File is '{}'", abs_file)

                ############################
                # Move file inside irods

                filename = None
                # Verify if the current path proposed from the user
                # is indeed an existing collection in iRODS
                if icom.is_collection(path):
                    # When should the original name be used?
                    # Only if the path specified is an
                    # existing irods collection
                    filename = original_filename

                try:
                    # Handling (iRODS) path
                    ipath = self.complete_path(path, filename)
                    log.verbose("Save into: {}", ipath)
                    iout = icom.save(
                        abs_file, destination=ipath, force=force, resource=resource
                    )
                    log.info("irods call {}", iout)
                finally:
                    # Transaction rollback: remove local cache in any case
                    log.debug("Removing cache object")
                    os.remove(abs_file)

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
                content = {'filename': ipath}
                errors = None
                status = hcodes.HTTP_OK_BASIC
            except BaseException as e:
                content = ""
                errors = {"Uploading failed": "{}".format(e)}
                status = hcodes.HTTP_SERVER_ERROR

        ###################
        # Reply to user
        if filename is None:
            filename = self.filename_from_path(path)

        pid_found = True
        if not errors:
            out = {}
            pid_parameter = self._args.get('pid_await')
            if pid_parameter and 'true' in pid_parameter.lower():
                # Shall we get the timeout from user?
                pid_found = False
                timeout = time.time() + 10  # seconds from now
                pid = ''
                while True:
                    out, _ = icom.get_metadata(ipath)
                    pid = out.get('PID')
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
                    status = hcodes.HTTP_OK_ACCEPTED
                    errors = [error_message]
                else:
                    pid_found = True

            # Get iRODS checksum
            obj = icom.get_dataobject(ipath)
            checksum = obj.checksum

            content = {
                'location': self.b2safe_location(ipath),
                'PID': out.get('PID'),
                'checksum': checksum,
                'filename': filename,
                'path': path,
                'link': self.httpapi_location(
                    ipath, api_path=CURRENT_MAIN_ENDPOINT, remove_suffix=path
                ),
            }

        if pid_found:
            return self.response(content, errors=errors, code=status)
        else:
            return self.response(
                content, errors=errors, code=hcodes.HTTP_OK_ACCEPTED
            )

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required(roles=['normal_user'])
    def patch(self, location):
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
        # Note: ignore resource, get new filename as 'newname'
        path, _, newfile, force = self.get_file_parameters(
            icom, path=location, newfile=True
        )

        if force:
            raise RestApiException(
                "This operation cannot be forced in B2SAFE iRODS data objects",
                status_code=hcodes.HTTP_BAD_REQUEST
            )

        if newfile is None or newfile.strip() == '':
            raise RestApiException(
                "New filename missing; use the 'newname' JSON parameter",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        # Get the base directory
        collection = icom.get_collection_from_path(location)
        # Set the new absolute path
        newpath = icom.get_absolute_path(newfile, root=collection)
        # Move in irods
        icom.move(location, newpath)

        return {
            'location': self.b2safe_location(newpath),
            'filename': newfile,
            'path': collection,
            'link': self.httpapi_location(
                newpath, api_path=CURRENT_MAIN_ENDPOINT, remove_suffix=location
            ),
        }

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required(roles=['normal_user'])
    def delete(self, location=None):
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

        icom = r.icommands
        # get parameters with defaults
        path, resource, filename, force = self.get_file_parameters(icom)

        ###################
        # Testing option to remove the whole content of current home
        if TESTING:
            if self._args.get('debugclean'):
                home = icom.get_user_home()
                files = icom.list(home)
                for key, obj in files.items():
                    icom.remove(
                        home + self._path_separator + obj['name'],
                        recursive=obj['object_type'] == 'collection',
                    )
                    log.debug("Removed {}", obj['name'])
                return "Cleaned"

        # TODO: only if it has a PID?
        raise RestApiException(
            "Data removal NOT allowed inside the 'registered' domain",
            status_code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED,
        )
