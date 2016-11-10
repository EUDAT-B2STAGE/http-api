# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.

Code to implement the /api/resources endpoint

Note:
Endpoints list and behaviour are available at:
https://github.com/EUDAT-B2STAGE/http-api/blob/metadata_parser/docs/user/endpoints.md

"""

from __future__ import absolute_import

import os
from .commons import EudatEndpoint
from ..services.uploader import Uploader
from ..services.irods.client import IrodsException
# from ..services.irods.translations import Irods2Graph
# from commons import htmlcodes as hcodes
from ...auth import authentication
# from ...confs import config
from flask import request, current_app
from commons import htmlcodes as hcodes
from commons.logs import get_logger, pretty_print

## // TO FIX for custom response:
# from .response import decorate
from .. import decorators as decorate

logger = get_logger(__name__)

## // TO FIX: build this from the WP6 mappings
CURRENT_B2SAFE_SERVER = 'b2safe.cineca.it'
CURRENT_B2SAFE_SERVER_CODE = 'a0'
INTERNAL_PATH_SEPARATOR = '/'


class EudatTest(EudatEndpoint):
    """
    A class to test development of internal parts,
    e.g. responses
    """

    @decorate.add_endpoint_parameter('test')
    @decorate.apimethod
    def get(self, location=None):
        """
        This works for all methods: GET, POST, PUT, PATCH, DELETE
        """
        data = {
            'path': location,
            'parameters': self.get_input(),
            'parameter': self.get_input(single_parameter='test'),
        }
        # return data
        return self.force_response(data)


###############################
# Classes

class BasicEndpoint(Uploader, EudatEndpoint):

    @authentication.authorization_required
    @decorate.add_endpoint_parameter('resource')
    @decorate.add_endpoint_parameter('download', ptype=bool, default=False)
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self, irods_location=None):
        """
        Download file from filename
        """

        ###################
        # BASIC INIT

        if irods_location is None:
            return self.force_response(
                errors={'location': 'Missing filepath inside URI for GET'})
        elif not irods_location.startswith(INTERNAL_PATH_SEPARATOR):
            irods_location = INTERNAL_PATH_SEPARATOR + irods_location

        # get the base objects
        icom, sql, user = self.init_endpoint()
        # get parameters with defaults
        path, resource, filename, force = \
            self.get_file_parameters(icom, path=irods_location)

#         ###################
#         # IN CASE WE USE THE GRAPH

#         # # Getting the list
#         # if uuid is None:
#         #     data = self.formatJsonResponse(graph.DigitalEntity.nodes.all())
#         #     return self.force_response(data)

#         # # If trying to use a path as file
#         # elif name[-1] == INTERNAL_PATH_SEPARATOR:
#         #     return self.force_response(
#         #         errors={'dataobject': 'No dataobject/file requested'})

#         # # Get filename and ipath from uuid using the graph
#         # try:
#         #     dataobj_node = graph.DigitalEntity.nodes.get(id=uuid)
#         # except graph.DigitalEntity.DoesNotExist:
#         #     return self.force_response(errors={uuid: 'Not found.'})
#         # collection_node = dataobj_node.belonging.all().pop()

        ###################
        # No graph...

        # note: this command will give irods error
        # if the current user does not have permissions
        is_collection = icom.is_collection(path)

        data = {}

        ###################
        # In case the user request the download of a specific file
        if self._args.get('download'):
            if is_collection:
                return self.force_response(
                    errors={'collection': 'Recursive download is not allowed'})

            if filename is None:
                filename = self.filename_from_path(path)
            abs_file = self.absolute_upload_file(filename, user)

            # Make sure you remove any cached version to get a fresh obj
            try:
# // TO FIX:
    # decide if we want to use a cache, and how!
    # maybe nginx cache is better instead of our own?
                os.remove(abs_file)
            except:
                pass
            # Execute icommand (transfer data to cache)
            icom.open(path, abs_file)
            # Download the file from local fs
            filecontent = super().download(
                filename, subfolder=user, get=True)
            # Remove local file
            os.remove(abs_file)
            # Stream file content
            return filecontent

        ###################
        # data listing
        else:

            if is_collection:
                data = icom.list_as_json(root=path)
                if len(data) < 1:
                    data = []
                # Print content list if it's a collection
            else:
                # Print file details/sys metadata if it's a specific file
                data = icom.meta_sys_list(path)
                # if a path that does not exist
                if len(data) < 1:
                    return self.force_response(errors={
                        'not found':
                        "path does not exists or you don't have privileges"},
                        code=hcodes.HTTP_BAD_NOTFOUND)

                ## // TO FIX:
                # to be better parsed

            # what if does not exist?
            print("TEST", data, len(data))

        return data

    @authentication.authorization_required
    @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.add_endpoint_parameter('path')  # should contain the filename too
    @decorate.add_endpoint_parameter('resource')
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
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
            return self.force_response(
                errors={
                    'Forbidden path inside URI':
                    "Please pass the location string as parameter 'path'"
                },
                code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
            )

        # Disable upload for POST method
        if 'file' in request.files:
            return self.force_response(
                errors={
                    'File upload forbidden for this method':
                    'Please use the PUT method for this operation'
                },
                code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
            )

        ###################
        # BASIC INIT

        # get the base objects
        icom, sql, user = self.init_endpoint()
        # get parameters with defaults
        path, resource, filename, force = self.get_file_parameters(icom)

        # if path variable empty something is wrong
        if path is None:
            return self.force_response(
                errors={
                    'Path to remote resource is wrong':
                    'Note: only absolute paths are allowed'
                },
                code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
            )

        ###################
        # Create Directory

        base_url = request.url
        # remove from current request any parameters
        post_delimiter = '?'
        if post_delimiter in request.url:
            base_url = request.url[:request.url.index(post_delimiter)]

        # Create directory if not exists
        ipath = icom.create_empty(
            path, directory=True, ignore_existing=force
        )
        logger.info("Created irods collection: %s", ipath)
        status = hcodes.HTTP_OK_BASIC
        content = {
            'location': 'irods:///%s/%s/' % (
                CURRENT_B2SAFE_SERVER, path.lstrip(INTERNAL_PATH_SEPARATOR)),
            'path': path,
            'link': '%s/?path=%s' % (base_url, path)
        }

        return self.force_response(content, code=status)

    @authentication.authorization_required
    @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.add_endpoint_parameter('resource')
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def put(self, irods_location=None):
        """
        Handle file upload.

        Test on docker client shell with:
        http --form PUT $SERVER/api/resources/tempZone/home/guest/test \
            file@/tmp/gettoken force=True "$AUTH"

        PUT request to upload a file not working in Flask:
        http://stackoverflow.com/a/9533843/2114395

        Note to developers:
        iRODS does not allow to do iput on more than one resource.
        To put the second one you will need the irepl command, which
        will assure that we have a replica on all resources.
        """

# // TO FIX:
# this is also used inside the delete method
# we may consider moving this block inside the `get_file_parameters` method
        if irods_location is None:
            return self.force_response(
                errors={'location': 'Missing filepath inside URI for PUT'})
        elif not irods_location.startswith(INTERNAL_PATH_SEPARATOR):
            irods_location = INTERNAL_PATH_SEPARATOR + irods_location

        ###################
        # BASIC INIT

        # get the base objects
        icom, sql, user = self.init_endpoint()
        # get parameters with defaults
        path, resource, filename, force = \
            self.get_file_parameters(icom, path=irods_location)

        # Disable directory creation for PUT method
        if 'file' not in request.files:
            return self.force_response(
                errors={
                    'Directory creation is forbidden for this method':
                    'Please use the POST method for this operation'
                },
                code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED
            )

        # Normal upload: inside the host tmp folder
        response = super(BasicEndpoint, self) \
            .upload(subfolder=user, force=force)

        # Check if upload response is success
## // TO FIX:
# this piece of code does not work with a custom response
# if it changes the main blocks of the json root;
# same developer should be able to provide a 'custom_split' on it
        content, errors, status = \
            self.get_content_from_response(response, get_all=True)

        ###################
        # If files uploaded
        key_file = 'filename'
        if isinstance(content, dict) and key_file in content:

            original_filename = content[key_file]

            abs_file = self.absolute_upload_file(original_filename, user)
            logger.info("File is '%s'" % abs_file)

            ############################
            # Move file inside irods

            filename = None
            # Verify if the current path proposed from the user
            # is indeed an existing collection in iRODS
            if icom.is_collection(path):
                # When should the original name be used?
                # Only if the path specified is an existing irods collection
                filename = original_filename

            ipath = None
            try:
                # Handling (iRODS) path
                ipath = self.complete_path(path, filename)
                # ipath = icom.get_irods_path(path, filename)

                iout = icom.save(
                    abs_file,
                    destination=path, force=force, resource=resource)
                logger.info("irods call %s", iout)
            finally:
                # Transaction rollback: remove local cache in any case
                logger.debug("Removing cache object")
                os.remove(abs_file)

            ###################
            # ## GRAPH DB - not included in the pre-production release
            # # Call internally the POST method for DO endpoint
            # location = None
            # doid = BasicEndpoint()._post(graph, graphuser, location)
            # # Return link to the file /api/resources/<DOID>

            ###################
            # Reply to user

            link = "%s://%s%s%s" % (
                request.environ['wsgi.url_scheme'],
                request.environ['HTTP_HOST'],
                str(request.url_rule)
                .split('<')[0].rstrip(INTERNAL_PATH_SEPARATOR),
                ipath
            )

            if filename is None:
                filename = self.filename_from_path(path)

            content = {
                'location': 'irods:///%s/%s' %
                (CURRENT_B2SAFE_SERVER, ipath.lstrip(INTERNAL_PATH_SEPARATOR)),
                'filename': filename,
                'path': path,
                'resources': icom.get_resources_from_file(ipath),
                # 'link': '%s/%s?path=%s' % (request.url, filename, path)
                'link': link
            }

        # pretty_print(content)
        return self.force_response(content, errors=errors, code=status)

    @authentication.authorization_required
    @decorate.add_endpoint_parameter('resource')
    @decorate.add_endpoint_parameter('debugclean')
    # @authentication.authorization_required(roles=config.ROLE_INTERNAL)
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def delete(self, irods_location=None):
        """
        Remove an object or an empty directory on iRODS

        http DELETE \
            $SERVER/api/resources/tempZone/home/guest/test/filename "$AUTH"
        """

        ###################
        # BASIC INIT

        # get the base objects
        icom, sql, user = self.init_endpoint()
        # get parameters with defaults
        path, resource, filename, force = self.get_file_parameters(icom)

        ###################
        # Debug/Testing option to remove the whole content of current home
        if current_app.config['DEBUG'] or current_app.config['TESTING']:
            if self._args.get('debugclean'):
                icom, sql, user = self.init_endpoint()
                home = icom.get_user_home(user)
                files = icom.list_as_json(home)
                for key, obj in files.items():
                    icom.remove(
                        home + INTERNAL_PATH_SEPARATOR + obj['name'],
                        recursive=obj['object_type'] == 'collection')
                    logger.debug("Removed %s" % obj['name'])
                return "Cleaned"

        ###################
        # URI parameter is required
        if irods_location is None:
            return self.force_response(
                errors={'location': 'Missing path inside URI for DELETE'},
                code=hcodes.HTTP_BAD_REQUEST)
        elif not irods_location.startswith(INTERNAL_PATH_SEPARATOR):
            irods_location = INTERNAL_PATH_SEPARATOR + irods_location

        ########################################
        # # Get the dataobject from the graph
        # graph = self.global_get_service('neo4j')
        # dataobj_node = graph.DigitalEntity.nodes.get(id=uuid)
        # collection_node = dataobj_node.belonging.all().pop()

        # ipath = icom.get_irods_path(
        #     collection_node.path, dataobj_node.filename)

        # # Remove from graph:
        # # Delete with neomodel the dataobject
        # try:
        #     dataobj_node.delete()
        # except graph.DigitalEntity.DoesNotExist:
        #     return self.force_response(errors={uuid: 'Not found.'})

        # # Delete collection if not linked to any dataobject anymore?
        # if len(collection_node.belongs.all()) < 1:
        #     collection_node.delete()

        ########################################
        # Remove from irods (only files and empty directories)
        is_recursive = False
        if icom.is_collection(irods_location):
            if not icom.list_as_json(root=irods_location):
                # nb: recursive option is necessary to remove a collection
                is_recursive = True
            else:
                logger.info("list:  %i", len(icom.list(path=irods_location)))
                return self.force_response(
                    errors={'Directory is not empty':
                            'Only empty directories can be deleted'},
                    code=hcodes.HTTP_BAD_REQUEST)
        else:
                # Print file details/sys metadata if it's a specific file
                data = icom.meta_sys_list(irods_location)
                # if a path that does not exist
                if len(data) < 1:
                    return self.force_response(errors={
                        'not found':
                        "path does not exists or you don't have privileges"},
                        code=hcodes.HTTP_BAD_NOTFOUND)

        icom.remove(irods_location, recursive=is_recursive, resource=resource)
        logger.info("Removed %s", irods_location)

        return self.force_response({'requested removal': irods_location})
