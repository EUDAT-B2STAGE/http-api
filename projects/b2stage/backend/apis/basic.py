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
    def get(self, irods_location=None):
        """ Download file from filename """

        data = {}
        checksum = None

        if irods_location is None:
            return self.send_errors(
                'Location: missing filepath inside URI',
                code=hcodes.HTTP_BAD_REQUEST)
        irods_location = self.fix_location(irods_location)

        ###################
        # Init EUDAT endpoint resources
        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors)

        # get parameters with defaults
        icom = r.icommands
        path, resource, filename, force = \
            self.get_file_parameters(icom, path=irods_location)

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
                    return icom.read_in_streaming(path)

        ###################
        # DATA LISTING
        ###################

        EMPTY_RESPONSE = {}

        #####################
        # DIRECTORY
        if is_collection:
            collection = path
            data = icom.list(path=collection)
            if len(data) < 1:
                data = EMPTY_RESPONSE
            # Print content list if it's a collection
        #####################
        # FILE (or not existing)
        else:
            collection = icom.get_collection_from_path(path)
            current_filename = path[len(collection) + 1:]

            from contextlib import suppress
            with suppress(IrodsException):
                filelist = icom.list(path=collection)
                data = EMPTY_RESPONSE
                for filename, metadata in filelist.items():
                    if filename == current_filename:
                        data[filename] = metadata
                # log.pp(data)

            # # Print file details/sys metadata if it's a specific file
            # data = icom.meta_sys_list(path)

            # if a path that does not exist
            if len(data) < 1:
                return self.send_errors(
                    "Path does not exists or you don't have privileges: %s"
                    % path, code=hcodes.HTTP_BAD_NOTFOUND)

        # Set the right context to each element
        response = []
        for filename, metadata in data.items():

            # Get iRODS checksum
            file_path = os.path.join(collection, filename)
            try:
                obj = icom.get_dataobject(file_path)
                checksum = obj.checksum
            except IrodsException:
                checksum = None

            # Get B2SAFE metadata
            out = {}
            try:
                out, _ = icom.get_metadata(file_path)
            except IrodsException:
                pass

            metadata['checksum'] = checksum
            metadata['PID'] = out.get("PID")

            # Shell we add B2SAFE metadata only if present?
            metadata['EUDAT/FIXED_CONTENT'] = out.get("EUDAT/FIXED_CONTENT")
            metadata['EUDAT/REPLICA'] = out.get("EUDAT/REPLICA")
            metadata['EUDAT/FIO'] = out.get("EUDAT/FIO")
            metadata['EUDAT/ROR'] = out.get("EUDAT/ROR")
            metadata['EUDAT/PARENT'] = out.get("EUDAT/PARENT")

            metadata.pop('path')
            content = {
                'metadata': metadata,
                metadata['object_type']: filename,
                'path': collection,
                'location': self.b2safe_location(collection),
                'link': self.httpapi_location(
                    icom.get_absolute_path(filename, root=collection),
                    api_path=CURRENT_MAIN_ENDPOINT,
                    remove_suffix=irods_location)
            }

            response.append({filename: content})

        return response

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def post(self, irods_location=None):
        """
        Handle [directory creation](docs/user/registered.md#post).
        Test on internal client shell with:
        http --form POST \
            $SERVER/api/resources?path=/tempZone/home/guest/test \
            force=True "$AUTH"
        """

        # Post does not accept the <ID> inside the URI
        if irods_location is not None:
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
        if force:
            # TODO: implement recursion
            return self.send_errors(
                'Recursive collection creations has not yet been implemented',
                code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
            )

        # Create directory if not exists
        ipath = icom.create_empty(
            path, directory=True, ignore_existing=force
        )
        if ipath is None:
            if force:
                ipath = path
            else:
                raise IrodsException("Failed to create %s" % path)
        else:
            log.info("Created irods collection: %s", ipath)

        # TOFIX: Should this status be No response?
        status = hcodes.HTTP_OK_BASIC
        content = {
            'location': self.b2safe_location(path),
            'path': path,
            'link': self.httpapi_location(path, api_path=CURRENT_MAIN_ENDPOINT)
        }

        return self.force_response(content, code=status)

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def put(self, irods_location=None):
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

        if irods_location is None:
            return self.send_errors('Location: missing filepath inside URI',
                                    code=hcodes.HTTP_BAD_REQUEST)
        irods_location = self.fix_location(irods_location)
        # NOTE: irods_location will act strange due to Flask internals
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
            self.get_file_parameters(icom, path=irods_location)

        ipath = None

        # Manage both form and streaming upload

        #################
        # FORM UPLOAD
        if request.mimetype != 'application/octet-stream':
            # TODO: double check if this is the right mimetype

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

                abs_file = self.absolute_upload_file(original_filename,
                                                     r.username)
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
        # STREAMING UPLOAD
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
            except Exception as e:
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
                         " the object registration maybe in progress."
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
    def patch(self, irods_location=None):
        """
        PATCH a record. E.g. change only the filename to a resource.
        """

        if irods_location is None:
            return self.send_errors('Location: missing filepath inside URI',
                                    code=hcodes.HTTP_BAD_REQUEST)
        irods_location = self.fix_location(irods_location)

        ###################
        # BASIC INIT
        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors)
        icom = r.icommands
        # Note: ignore resource, get new filename as 'newname'
        path, _, newfile, force = \
            self.get_file_parameters(icom, path=irods_location, newfile=True)

        if force:
            return self.send_errors(
                "This operation cannot be forced in B2SAFE iRODS data objects",
                code=hcodes.HTTP_BAD_REQUEST)

        if newfile is None or newfile.strip() == '':
            return self.send_errors(
                "New filename missing; use the 'newname' JSON parameter",
                code=hcodes.HTTP_BAD_REQUEST)

        # Get the base directory
        collection = icom.get_collection_from_path(irods_location)
        # Set the new absolute path
        newpath = icom.get_absolute_path(newfile, root=collection)
        # Move in irods
        icom.move(irods_location, newpath)

        return {
            'location': self.b2safe_location(newpath),
            'filename': newfile,
            'path': collection,
            'link': self.httpapi_location(
                newpath,
                api_path=CURRENT_MAIN_ENDPOINT,
                remove_suffix=irods_location
            )
        }

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def delete(self, irods_location=None):
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

        # Note: this check is not at the beginning to allow the clean operation
        if irods_location is None:
            return self.send_errors('Location: missing filepath inside URI',
                                    code=hcodes.HTTP_BAD_REQUEST)
        irods_location = self.fix_location(irods_location)

        ########################################
        # Remove from irods (only files and empty directories)
        is_recursive = False
        if icom.is_collection(irods_location):
            if not icom.list(irods_location):
                # nb: recursive option is necessary to remove a collection
                is_recursive = True
            else:
                log.info("list:  %i", len(icom.list(path=irods_location)))
                return self.send_errors(
                    'Directory is not empty',
                    code=hcodes.HTTP_BAD_REQUEST)
        else:
            # Print file details/sys metadata if it's a specific file
            try:
                icom.get_metadata(path=irods_location)
            except IrodsException:
                # if a path that does not exist
                return self.send_errors(
                    "Path does not exists or you don't have privileges",
                    code=hcodes.HTTP_BAD_NOTFOUND)

        icom.remove(irods_location, recursive=is_recursive, resource=resource)
        log.info("Removed %s", irods_location)
        return {'removed': irods_location}
