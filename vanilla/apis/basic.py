# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.

Code to implement the /api/resources endpoint

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/metadata_parser/docs/user/endpoints.md

"""

import os
import irods
import time
from flask import request, current_app

from eudat.apis.common import PRODUCTION
from eudat.apis.common.b2stage import EudatEndpoint

from rapydo.services.uploader import Uploader
from flask_ext.flask_irods.client import IrodsException
# from ..services.irods.translations import Irods2Graph
from rapydo.utils import htmlcodes as hcodes
from rapydo import decorators as decorate
from rapydo.utils.logs import get_logger

log = get_logger(__name__)


###############################
# Classes

class BasicEndpoint(Uploader, EudatEndpoint):

    @decorate.catch_error(
        exception=IrodsException,
        error_code=hcodes.HTTP_BAD_NOTFOUND, exception_label='B2SAFE')
    def get(self, irods_location=None):
        """ Download file from filename """

        data = {}

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
        if not is_collection:
            icom.dataobject_exists(path)

        ###################
        # DOWNLOAD a specific file
        ###################

        if self._args.get('download'):
            # TO FIX: problem with swagger-ui boolean?
            if is_collection:
                return self.send_errors(
                    'collection', 'Recursive download is not allowed')

            if filename is None:
                filename = self.filename_from_path(path)
            abs_file = self.absolute_upload_file(filename, r.username)

            # TODO: decide if we want to use a cache when streaming
            # what about nginx caching?

            # Make sure you remove any cached version to get a fresh obj
            try:
                os.remove(abs_file)
            except BaseException:
                pass
            # Execute icommand (transfer data to cache)
            icom.open(path, abs_file)
            # Download the file from local fs
            filecontent = super().download(
                filename, subfolder=r.username, get=True)
            # Remove local file
            os.remove(abs_file)
            # Stream file content
            return filecontent

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
                    'not found',
                    "path does not exists or you don't have privileges",
                    code=hcodes.HTTP_BAD_NOTFOUND)

        # Get PID and Checksum
        try:
            out, _ = icom.get_metadata(path)
        except irods.exception.CollectionDoesNotExist:
            out = {}
        pid = out.get("PID")
        checksum = out.get("checksum")

        # Set the right context to each element
        response = []
        for filename, metadata in data.items():

            metadata.pop('path')

            response.append({
                filename: {
                    'metadata': metadata,
                    metadata['object_type']: filename,
                    metadata['PID']: pid,
                    metadata['checksum']: checksum,
                    'path': collection,
                    'location': self.b2safe_location(collection),
                    'link': self.httpapi_location(
                        request.url,
                        icom.get_absolute_path(filename, root=collection),
                        remove_suffix=irods_location)
                }
            })

        return response

#     @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def post(self, irods_location=None):
#         """
#         Handle [directory creation](docs/user/registered.md#post).
        pass

#         Test on internal client shell with:
#         http --form POST \
#             $SERVER/api/resources?path=/tempZone/home/guest/test \
#             force=True "$AUTH"
#         """

#         # Post does not accept the <ID> inside the URI
#         if irods_location is not None:
#             return self.send_errors(
#                 'Forbidden path inside URI',
#                 "Please pass the location string as parameter 'path'",
#                 code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
#             )

#         # Disable upload for POST method
#         if 'file' in request.files:
#             return self.send_errors(
#                 'File upload forbidden for this method',
#                 'Please use the PUT method for this operation',
#                 code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
#             )

#         ###################
#         # BASIC INIT

#         # get the base objects
#         r = self.init_endpoint()
#         # log.pp(r)
#         if r.errors is not None:
#             return self.send_errors(errors=r.errors)
#         icom = r.icommands
#         # get parameters with defaults
#         path, resource, filename, force = self.get_file_parameters(icom)

#         # if path variable empty something is wrong
#         if path is None:
#             return self.send_errors(
#                 'Path to remote resource',
#                 'Note: only absolute paths are allowed',
#                 code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
#             )

#         ###################
#         # Create Directory

#         # Create directory if not exists
#         ipath = icom.create_empty(
#             path, directory=True, ignore_existing=force
#         )
#         log.info("Created irods collection: %s", ipath)

#         # TO FIX: Should this status be No response?
#         status = hcodes.HTTP_OK_BASIC
#         content = {
#             'location': self.b2safe_location(ipath),
#             'path': ipath,
#             'link': self.httpapi_location(request.url, ipath)
#         }

#         return self.force_response(content, code=status)

#     @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def put(self, irods_location=None):
#         """
#         Handle file upload. Test on docker client shell with:
#         http --form PUT $SERVER/api/resources/tempZone/home/guest/test \
#             file@/tmp/gettoken force=True "$AUTH"
        pass

#         Note to devs: iRODS does not allow to iput on more than one resource.
#         To put the second one you need the irepl command,
#         which will assure that we have a replica on all resources...
#         """

#         if irods_location is None:
#             return self.send_errors('location', 'Missing filepath inside URI',
#                                     code=hcodes.HTTP_BAD_REQUEST)
#         irods_location = self.fix_location(irods_location)

#         ###################
#         # BASIC INIT

#         # get the base objects
#         r = self.init_endpoint()
#         # log.pp(r)
#         if r.errors is not None:
#             return self.send_errors(errors=r.errors)
#         icom = r.icommands
#         # get parameters with defaults
#         path, resource, filename, force = \
#             self.get_file_parameters(icom, path=irods_location)

#         # Disable directory creation for PUT method
#         if 'file' not in request.files:
#             return self.send_errors(
#                 'Directory creation is forbidden for this method',
#                 'Please use the POST method for this operation',
#                 code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
#             )

#         # Normal upload: inside the host tmp folder
#         response = super(BasicEndpoint, self) \
#             .upload(subfolder=r.username, force=force)

#         # Check if upload response is success
# #  TO FIX: custom split of a custom response
# # this piece of code does not work with a custom response
# # if it changes the main blocks of the json root;
# # the developer should be able to provide a 'custom_split' on this
#         content, errors, status = \
#             self.explode_response(response, get_all=True)

#         ###################
#         # If files uploaded
#         key_file = 'filename'
#         if isinstance(content, dict) and key_file in content:

#             original_filename = content[key_file]

#             abs_file = self.absolute_upload_file(original_filename, r.username)
#             log.info("File is '%s'" % abs_file)

#             ############################
#             # Move file inside irods

#             filename = None
#             # Verify if the current path proposed from the user
#             # is indeed an existing collection in iRODS
#             if icom.is_collection(path):
#                 # When should the original name be used?
#                 # Only if the path specified is an existing irods collection
#                 filename = original_filename

#             ipath = None
#             try:
#                 # Handling (iRODS) path
#                 ipath = self.complete_path(path, filename)
#                 # ipath = icom.get_irods_path(path, filename)

#                 iout = icom.save(
#                     abs_file,
#                     destination=path, force=force, resource=resource)
#                 log.info("irods call %s", iout)
#             finally:
#                 # Transaction rollback: remove local cache in any case
#                 log.debug("Removing cache object")
#                 os.remove(abs_file)

#             ###################
#             # ## GRAPH DB - not included in the pre-production release
#             # # Call internally the POST method for DO endpoint
#             # location = None
#             # doid = BasicEndpoint()._post(graph, graphuser, location)
#             # # Return link to the file /api/resources/<DOID>

#             ###################
#             # Reply to user

#             if filename is None:
#                 filename = self.filename_from_path(path)

#             # link = "%s://%s%s%s" % (
#             #     request.environ['wsgi.url_scheme'],
#             #     request.environ['HTTP_HOST'],
#             #     str(request.url_rule)
#             #     .split('<')[0].rstrip(self._path_separator),
#             #     ipath
#             # )

#             if self._args.get('pid'):
#                 # Shall we get the timeout from user?
#                 timeout = time.time() + 60  # 1 minute from now
#                 pid = ''
#                 while True:
#                     out, _ = icom.get_metadata(path)
#                     pid = out.get('PID')
#                     if pid != '' or time.time() > timeout:
#                         break
#                     time.sleep(2)

#             content = {
#                 'location': self.b2safe_location(ipath),
#                 'PID': out.get('PID'),
#                 'EUDAT/CHECKSUM': out.get('EUDAT/CHECKSUM'),
#                 'filename': filename,
#                 'path': path,
#                 'link': self.httpapi_location(request.url, ipath, path)
#             }

#         # log.pp(content)
#         return self.force_response(content, errors=errors, code=status)

#     @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def patch(self, irods_location=None):
#         """
#         PATCH a record. E.g. change only the filename to a resource.
#         """
        pass

#         if irods_location is None:
#             return self.send_errors('location', 'Missing filepath inside URI',
#                                     code=hcodes.HTTP_BAD_REQUEST)
#         irods_location = self.fix_location(irods_location)

#         ###################
#         # BASIC INIT
#         r = self.init_endpoint()
#         if r.errors is not None:
#             return self.send_errors(errors=r.errors)
#         icom = r.icommands
#         # Note: ignore resource, get new filename as 'newname'
#         path, _, newfile, force = \
#             self.get_file_parameters(icom, path=irods_location, newfile=True)

#         if newfile is None or newfile.strip() == '':
#             return self.send_errors(
#                 'New filename missing', "Use the 'newname' JSON parameter",
#                 code=hcodes.HTTP_BAD_REQUEST)

#         # Get the base directory
#         collection = icom.get_collection_from_path(irods_location)
#         # Set the new absolute path
#         newpath = icom.get_absolute_path(newfile, root=collection)
#         # Move in irods
#         icom.move(irods_location, newpath)

#         return {
#             'location': self.b2safe_location(newpath),
#             'filename': newfile,
#             'path': collection,
#             'link': self.httpapi_location(request.url, newpath, irods_location)
#         }

#     @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def delete(self, irods_location=None):
#         """
#         Remove an object or an empty directory on iRODS

#         http DELETE \
#             $SERVER/api/resources/tempZone/home/guest/test/filename "$AUTH"
#         """
        pass

#         ###################
#         # BASIC INIT

#         # get the base objects
#         r = self.init_endpoint()
#         # log.pp(r)
#         if r.errors is not None:
#             return self.send_errors(errors=r.errors)
#         icom = r.icommands
#         # get parameters with defaults
#         path, resource, filename, force = self.get_file_parameters(icom)

#         ###################
#         # Debug/Testing option to remove the whole content of current home
#         if not PRODUCTION or current_app.config['TESTING']:
#             if self._args.get('debugclean'):
#                 home = icom.get_user_home()
#                 files = icom.list_as_json(home)
#                 for key, obj in files.items():
#                     icom.remove(
#                         home + self._path_separator + obj['name'],
#                         recursive=obj['object_type'] == 'collection')
#                     log.debug("Removed %s" % obj['name'])
#                 return "Cleaned"

#         # Note: this check is not at the beginning to allow the clean operation
#         if irods_location is None:
#             return self.send_errors('location', 'Missing filepath inside URI',
#                                     code=hcodes.HTTP_BAD_REQUEST)
#         irods_location = self.fix_location(irods_location)

#         ########################################
#         # # Get the dataobject from the graph
#         # graph = self.neo
#         # dataobj_node = graph.DigitalEntity.nodes.get(id=uuid)
#         # collection_node = dataobj_node.belonging.all().pop()

#         # ipath = icom.get_irods_path(
#         #     collection_node.path, dataobj_node.filename)

#         # # Remove from graph:
#         # # Delete with neomodel the dataobject
#         # try:
#         #     dataobj_node.delete()
#         # except graph.DigitalEntity.DoesNotExist:
#         #     return self.send_errors(uuid, 'Not found.')

#         # # Delete collection if not linked to any dataobject anymore?
#         # if len(collection_node.belongs.all()) < 1:
#         #     collection_node.delete()

#         ########################################
#         # Remove from irods (only files and empty directories)
#         is_recursive = False
#         if icom.is_collection(irods_location):
#             if not icom.list_as_json(root=irods_location):
#                 # nb: recursive option is necessary to remove a collection
#                 is_recursive = True
#             else:
#                 log.info("list:  %i", len(icom.list(path=irods_location)))
#                 return self.send_errors(
#                     'Directory is not empty',
#                     'Only empty directories can be deleted',
#                     code=hcodes.HTTP_BAD_REQUEST)
#         else:
#             # Print file details/sys metadata if it's a specific file
#             data = icom.meta_sys_list(irods_location)
#             # if a path that does not exist
#             if len(data) < 1:
#                 return self.send_errors(
#                     'not found',
#                     "path does not exists or you don't have privileges",
#                     code=hcodes.HTTP_BAD_NOTFOUND)

#         icom.remove(irods_location, recursive=is_recursive, resource=resource)
#         log.info("Removed %s", irods_location)

#         return {'removed': irods_location}
