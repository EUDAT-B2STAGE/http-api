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
from .. import decorators as decorate
from ...auth import authentication
# from ...confs import config
from flask import request
from commons import htmlcodes as hcodes
from commons.logs import get_logger, pretty_print

logger = get_logger(__name__)

## // TO FIX: build this from the WP6 mappings
CURRENT_B2SAFE_SERVER = 'b2safe.cineca.it'
CURRENT_B2SAFE_SERVER_CODE = 'a0'


# class EudatTest(EudatEndpoint):

#     @decorate.add_endpoint_parameter('test')
#     @decorate.apimethod
#     def get(self, location=None):
#         """
#         This works for all methods: GET, POST, PUT, PATCH, DELETE
#         """
#         data = {
#             'path': location,
#             'parameters': self.get_input(),
#             'parameter': self.get_input(single_parameter='test'),
#         }
#         return data


###############################
# Classes

class BasicEndpoint(Uploader, EudatEndpoint):

    @authentication.authorization_required
    # @decorate.add_endpoint_parameter('path')
    @decorate.add_endpoint_parameter('resource')
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self, irods_location=None):
        """
        Download file from filename
        """

        return "TO BE IMPLEMENTED"

#         ###################
#         # BASIC INIT

#         # get the base objects
#         icom, sql, user = self.init_endpoint()
#         # get parameters with defaults
        path, resource, filename, force = self.get_file_parameters(icom)

#         ###################
#         # IN CASE WE USE THE GRAPH

#         # # Getting the list
#         # if uuid is None:
#         #     data = self.formatJsonResponse(graph.DigitalEntity.nodes.all())
#         #     return self.force_response(data)

#         # # If trying to use a path as file
#         # elif name[-1] == '/':
#         #     return self.force_response(
#         #         errors={'dataobject': 'No dataobject/file requested'})

#         # # Get filename and ipath from uuid using the graph
#         # try:
#         #     dataobj_node = graph.DigitalEntity.nodes.get(id=uuid)
#         # except graph.DigitalEntity.DoesNotExist:
#         #     return self.force_response(errors={uuid: 'Not found.'})
#         # collection_node = dataobj_node.belonging.all().pop()

#         # # irods paths
#         # ipath = icom.get_irods_path(
#         #     collection_node.path, dataobj_node.filename)

#         ###################
#         # In case we ask the list
#         if myname is None:
#             # files = icom.search(path.lstrip('/'), like=False)
# ## FIX with ils -r
#             files = icom.list(path)
#             print(files)
#             return "GET ALL"

#         ###################
#         # In case we download a specific file

#         # ipath = icom.get_irods_path(path, myname)
#         # print("TEST", ipath)

#         abs_file = self.absolute_upload_file(myname, user)

# # // TO FIX:
# # decide if we want to use a cache, and how
# # note: maybe nginx instead of our own
#         # Make sure you remove any cached version to get a fresh obj
#         try:
#             os.remove(abs_file)
#         except:
#             pass

#         print("TEST", abs_file)

#     #     # Execute icommand (transfer data to cache)
#     #     icom.open(ipath, abs_file)

#     #     # Download the file from local fs
#     #     filecontent = super().download(
#     #         dataobj_node.filename, subfolder=user, get=True)

#     #     # Remove local file
#     #     os.remove(abs_file)

#         return "GET " + myname

#     #     # Stream file content
#     #     return filecontent

    @authentication.authorization_required
    @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.add_endpoint_parameter('path')  # should contain the filename too
    @decorate.add_endpoint_parameter('resource')
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def post(self):
        """
        Handle [directory creation](docs/user/registered.md#post).

        Test on docker client shell with:
        http --form POST $SERVER/api/resources \
            force=True path=/tempZone/home/guest/test "$AUTH"
        """

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
                code=hcodes.HTTP_NOT_IMPLEMENTED
            )

        ###################
        # UPLOADER
        content = None
        errors = {}
        status = None

        base_url = request.url
        # remove from current request any parameters
        post_delimiter = '?'
        if post_delimiter in request.url:
            base_url = request.url[:request.url.index(post_delimiter)]

        # Create directory if not exists
        ipath = icom.create_empty(
            path, directory=True, ignore_existing=force)
        logger.info("Created irods collection: %s", ipath)
        status = hcodes.HTTP_OK_BASIC
        content = {
            'location': 'irods:///%s/%s/' % (
                CURRENT_B2SAFE_SERVER, path.lstrip('/')),
            'path': path,
            'link': '%s/?path=%s' % (base_url, path)
        }

        return self.force_response(content, errors=errors, code=status)

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

        if irods_location is None:
            return self.force_response(
                errors={'location': 'Missing filepath inside URI for PUT'})

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

        # If response is success, save inside the database
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

            # The user may decide a different name for the uploaded file
            # otherwise we use the original name from the file itself
            if filename is None:
                filename = original_filename

            # Handling iRODS path
            ipath = icom.get_irods_path(path, filename)

            try:
                iout = icom.save(abs_file, destination=ipath,
                                 force=force, resource=resource)
                logger.info("irods call %s", iout)
            finally:
                # Remove local cache in any case
                os.remove(abs_file)

# # GRAPH?
#             # Call internally the POST method for DO endpoint
#             location = None
#             doid = DigitalObjectsEndpoint()._post(graph, graphuser, location)
#             # Return link to the file /api/digitalobjects/DOID/entities/EID

            ###################
            # Reply to user

            content = {
                'location': 'irods:///%s/%s/%s' % (
                    CURRENT_B2SAFE_SERVER,
                    # request.url.lstrip('http://'),
                    path.lstrip('/'), filename),
                'filename': filename,
                'path': path,
                'resources': icom.get_resources_from_file(ipath),
                'link': '%s/%s?path=%s' % (request.url, filename, path)
            }

        pretty_print(content)
        return self.force_response(content, errors=errors, code=status)

    @authentication.authorization_required
    # @decorate.add_endpoint_parameter('path')
    @decorate.add_endpoint_parameter('resource')
    # @authentication.authorization_required(roles=config.ROLE_INTERNAL)
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def delete(self, irods_location=None):
        """
        Remove an object

        http DELETE \
            $SERVER/api/digitalentities/gettoken?resource=replicaResc "$AUTH"
        """

        return "TO BE IMPLEMENTED"

        # ###################
        # # BASIC INIT

        # # get the base objects
        # icom, sql, user = self.init_endpoint()
        # # get parameters with defaults
        path, resource, filename, force = self.get_file_parameters(icom)
        # # Handling iRODS path
        # ipath = icom.get_irods_path(path, filename)

        # ########################################
        # # # Get the dataobject from the graph
        # # graph = self.global_get_service('neo4j')
        # # dataobj_node = graph.DigitalEntity.nodes.get(id=uuid)
        # # collection_node = dataobj_node.belonging.all().pop()

        # # ipath = icom.get_irods_path(
        # #     collection_node.path, dataobj_node.filename)

        # # # Remove from graph:
        # # # Delete with neomodel the dataobject
        # # try:
        # #     dataobj_node.delete()
        # # except graph.DigitalEntity.DoesNotExist:
        # #     return self.force_response(errors={uuid: 'Not found.'})

        # # # Delete collection if not linked to any dataobject anymore?
        # # if len(collection_node.belongs.all()) < 1:
        # #     collection_node.delete()

        # ########################################
        # # Remove from irods
        # icom.remove(ipath, resource=resource)
        # logger.info("Removed %s", ipath)

        # return self.force_response({'requested removal': ipath})
