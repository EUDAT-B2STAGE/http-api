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
from flask import request, current_app
# from werkzeug import secure_filename

from b2stage.apis.commons import PRODUCTION, CURRENT_MAIN_ENDPOINT
from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi.services.uploader import Uploader
from restapi.flask_ext.flask_irods.client import IrodsException
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate
from utilities.logs import get_logger

log = get_logger(__name__)


###############################
# Classes

class BasicEndpoint(Uploader, EudatEndpoint):

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, location=None):
        """ Download file from filename """

        if location is None:
            return self.send_errors(
                'Location: missing filepath inside URI',
                code=hcodes.HTTP_BAD_REQUEST)
        location = self.fix_location(location)

        ###################
        # Init EUDAT endpoint resources
        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors)

        # get parameters with defaults
        icom = r.icommands
        path, resource, filename, force = \
            self.get_file_parameters(icom, path=location)

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
                    return self.send_errors(
                        'Collection: recursive download is not allowed')
                else:
                    # NOTE: we always send in chunks when downloading
                    return icom.read_in_streaming(path)

        return self.list_objects(icom, path, is_collection, location)

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def post(self, location=None):
        """
        Handle [directory creation](docs/user/registered.md#post).
        Test on internal client shell with:
        http --form POST \
            $SERVER/api/resources?path=/tempZone/home/guest/test \
            force=True "$AUTH"
        """

        # Post does not accept the <ID> inside the URI
        if location is not None:
            return self.send_errors(
                'Forbidden path inside URI; ' +
                "Please pass the location string as body parameter 'path'",
                code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
            )

        # Disable upload for POST method
        if 'file' in request.files:
            return self.send_errors(
                'File upload forbidden for this method; ' +
                'Please use the PUT method for this operation',
                code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
            )

        ###################
        # BASIC INIT
        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors)
        icom = r.icommands
        # get parameters with defaults
        path, resource, filename, force = self.get_file_parameters(icom)

        # if path variable empty something is wrong
        if path is None:
            return self.send_errors(
                'Path to remote resource: only absolute paths are allowed',
                code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
            )

        ###################
        # Create Directory

        ipath = icom.create_directory(path, ignore_existing=force)
        if ipath is None:
            if force:
                ipath = path
            else:
                raise IrodsException("Failed to create %s" % path)
        else:
            log.info("Created irods collection: %s", ipath)

        # NOTE: question: should this status be No response?
        status = hcodes.HTTP_OK_BASIC
        content = {
            'location': self.b2safe_location(path),
            'path': path,
            'link': self.httpapi_location(path, api_path=CURRENT_MAIN_ENDPOINT)
        }

        return self.force_response(content, code=status)

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def put(self, location=None):
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

        if location is None:
            return self.send_errors('Location: missing filepath inside URI',
                                    code=hcodes.HTTP_BAD_REQUEST)
        location = self.fix_location(location)
        # NOTE: location will act strange due to Flask internals
        # in case upload is served with streaming options,
        # NOT finding the right path + filename if the path is a collection

        ###################
        # Basic init
        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors)
        icom = r.icommands
        # get parameters with defaults
        path, resource, filename, force = \
            self.get_file_parameters(icom, path=location)

        # Manage both form and streaming upload
        ipath = None

        #################
        # CASE 1- FORM UPLOAD
        if request.mimetype != 'application/octet-stream':

            # Read the request
            request.get_data()

            # Normal upload: inside the host tmp folder
            response = super(BasicEndpoint, self) \
                .upload(subfolder=r.username, force=force)

            # Check if upload response is success
            content, errors, status = \
                self.explode_response(response, get_all=True)

            ###################
            # If files uploaded
            key_file = 'filename'

            if isinstance(content, dict) and key_file in content:
                original_filename = content[key_file]
                abs_file = self.absolute_upload_file(
                    original_filename, r.username)
                log.info("File is '%s'" % abs_file)

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
                    log.verbose("Save into: %s", ipath)
                    iout = icom.save(
                        abs_file,
                        destination=ipath, force=force, resource=resource)
                    log.info("irods call %s", iout)
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
                    destination=ipath, force=force, resource=resource)
                log.info("irods call %s", iout)
                response = self.force_response({'filename': ipath},
                                               code=hcodes.HTTP_OK_BASIC)
            except BaseException as e:
                response = self.force_response(
                    errors={"Uploading failed": "{0}".format(e)},
                    code=hcodes.HTTP_SERVER_ERROR)

            content, errors, status = \
                self.explode_response(response, get_all=True)

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
                    error_message = \
                        ("Timeout waiting for PID from B2SAFE:"
                         " the object registration may be still in progress."
                         " File correctly uploaded.")
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
                    ipath,
                    api_path=CURRENT_MAIN_ENDPOINT,
                    remove_suffix=path)
            }

        # log.pp(content)
        if pid_found:
            return self.force_response(content, errors=errors, code=status)
        else:
            return self.send_warnings(
                content, errors=errors, code=hcodes.HTTP_OK_ACCEPTED)

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def patch(self, location=None):
        """
        PATCH a record. E.g. change only the filename to a resource.
        """

        if location is None:
            return self.send_errors('Location: missing filepath inside URI',
                                    code=hcodes.HTTP_BAD_REQUEST)
        location = self.fix_location(location)

        ###################
        # BASIC INIT
        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors)
        icom = r.icommands
        # Note: ignore resource, get new filename as 'newname'
        path, _, newfile, force = \
            self.get_file_parameters(icom, path=location, newfile=True)

        if force:
            return self.send_errors(
                "This operation cannot be forced in B2SAFE iRODS data objects",
                code=hcodes.HTTP_BAD_REQUEST)

        if newfile is None or newfile.strip() == '':
            return self.send_errors(
                "New filename missing; use the 'newname' JSON parameter",
                code=hcodes.HTTP_BAD_REQUEST)

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
                newpath,
                api_path=CURRENT_MAIN_ENDPOINT,
                remove_suffix=location
            )
        }

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
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
        # log.pp(r)
        if r.errors is not None:
            return self.send_errors(errors=r.errors)
        icom = r.icommands
        # get parameters with defaults
        path, resource, filename, force = self.get_file_parameters(icom)

        ###################
        # Debug/Testing option to remove the whole content of current home
        if not PRODUCTION or current_app.config['TESTING']:
            if self._args.get('debugclean'):
                home = icom.get_user_home()
                files = icom.list(home)
                for key, obj in files.items():
                    icom.remove(
                        home + self._path_separator + obj['name'],
                        recursive=obj['object_type'] == 'collection')
                    log.debug("Removed %s" % obj['name'])
                return "Cleaned"

        # TODO: only if it has a PID?
        return self.send_errors(
            "Data objects/collections removal " +
            "is NOT allowed inside the 'registered' domain",
            code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
        )

        # # Note: check not at the beginning to allow the "clean" operation
        # if location is None:
        #     return self.send_errors('Location: missing filepath inside URI',
        #                             code=hcodes.HTTP_BAD_REQUEST)
        # location = self.fix_location(location)

        # ########################################
        # # Remove from irods (only files and empty directories)
        # is_recursive = False
        # if icom.is_collection(location):
        #     if not icom.list(location):
        #         # nb: recursive option is necessary to remove a collection
        #         is_recursive = True
        #     else:
        #         log.info("list:  %i", len(icom.list(path=location)))
        #         return self.send_errors(
        #             'Directory is not empty',
        #             code=hcodes.HTTP_BAD_REQUEST)
        # else:
        #     # Print file details/sys metadata if it's a specific file
        #     try:
        #         icom.get_metadata(path=location)
        #     except IrodsException:
        #         # if a path that does not exist
        #         return self.send_errors(
        #             "Path does not exists or you don't have privileges",
        #             code=hcodes.HTTP_BAD_NOTFOUND)

        # icom.remove(location, recursive=is_recursive, resource=resource)
        # log.info("Removed %s", location)
        # return {'removed': location}
