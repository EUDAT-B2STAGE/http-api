# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.

A digital entity is
...
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
from ...confs import config
from commons.logs import get_logger

logger = get_logger(__name__)


###############################
# Classes

class DigitalEntityEndpoint(Uploader, EudatEndpoint):

    @authentication.authorization_required
    @decorate.add_endpoint_parameter('path')
    @decorate.add_endpoint_parameter('resource')
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self, filename=None):
        """
        Download file from filename
        """

        ###################
        # BASIC INIT

        # get the base objects
        icom, sql, user = self.init_endpoint()
        # get parameters with defaults
        path, resource, myname = self.get_file_parameters(icom, filename)

        ###################
        # IN CASE WE USE THE GRAPH

        # # Getting the list
        # if uuid is None:
        #     data = self.formatJsonResponse(graph.DigitalEntity.nodes.all())
        #     return self.force_response(data)

        # # If trying to use a path as file
        # elif name[-1] == '/':
        #     return self.force_response(
        #         errors={'dataobject': 'No dataobject/file requested'})

        # # Get filename and ipath from uuid using the graph
        # try:
        #     dataobj_node = graph.DigitalEntity.nodes.get(id=uuid)
        # except graph.DigitalEntity.DoesNotExist:
        #     return self.force_response(errors={uuid: 'Not found.'})
        # collection_node = dataobj_node.belonging.all().pop()

        # # irods paths
        # ipath = icom.get_irods_path(
        #     collection_node.path, dataobj_node.filename)

        ###################
        # In case we ask the list
        if myname is None:
            # files = icom.search(path.lstrip('/'), like=False)
            files = icom.list(path)
            print(files)
            return "GET ALL"

        ###################
        # In case we download a specific file

        # ipath = icom.get_irods_path(path, myname)
        # print("TEST", ipath)

        abs_file = self.absolute_upload_file(myname, user)

# // TO FIX:
# decide if we want to use a cache, and how
# note: maybe nginx instead of our own
        # Make sure you remove any cached version to get a fresh obj
        try:
            os.remove(abs_file)
        except:
            pass

        print("TEST", abs_file)

    #     # Execute icommand (transfer data to cache)
    #     icom.open(ipath, abs_file)

    #     # Download the file from local fs
    #     filecontent = super().download(
    #         dataobj_node.filename, subfolder=user, get=True)

    #     # Remove local file
    #     os.remove(abs_file)

        return "GET " + myname

    #     # Stream file content
    #     return filecontent

    @authentication.authorization_required
    @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.add_endpoint_parameter('filename')
    @decorate.add_endpoint_parameter('path')
    @decorate.add_endpoint_parameter('resource')
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def post(self):
        """
        Handle file upload
        http --form POST localhost:8080/api/dataobjects \
            file@docker-compose.test.yml

        Test with:
    http --form POST $SERVER/api/entities file@/tmp/gettoken force=True "$AUTH"
        """

        ###################
        # BASIC INIT

        force = self._args.get('force')
        # get the base objects
        icom, sql, user = self.init_endpoint()
        # get parameters with defaults
        path, resource, filename = self.get_file_parameters(icom)
        # Original upload
        response = super(DigitalEntityEndpoint, self) \
            .upload(subfolder=user, force=force)

        ###################
        # If response is success, save inside the database
        key_file = 'filename'

        content, errors, status = \
            self.get_content_from_response(response, get_all=True)

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

            # ##HANDLING PATH
            # The home dir for the current user
            # Where to put the file in irods
            ipath = icom.get_irods_path(
                self._args.get('collection'), filename)

            try:
                iout = icom.save(
                    abs_file, destination=ipath, force=force)
                logger.info("irods call %s", iout)
            finally:
                # Remove local cache in any case
                os.remove(abs_file)

# # GRAPH?
#             # Call internally the POST method for DO endpoint
#             location = None
#             doid = DigitalObjectsEndpoint()._post(graph, graphuser, location)
#             # Return link to the file /api/digitalobjects/DOID/entities/EID

        # Reply to user
# // TO FIX:
## BUILD LOCATION
        content = "TO BE COMPLETED... should return: " + \
            "location, resource, path, filename"

        return self.force_response(content, errors=errors, code=status)

    @authentication.authorization_required(roles=config.ROLE_INTERNAL)
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def delete(self, filename=None):
        """ Remove an object """

        pass

    #     # Get the dataobject from the graph
    #     graph = self.global_get_service('neo4j')
    #     dataobj_node = graph.DigitalEntity.nodes.get(id=uuid)
    #     collection_node = dataobj_node.belonging.all().pop()

    #     icom = self.global_get_service('irods')
    #     ipath = icom.get_irods_path(
    #         collection_node.path, dataobj_node.filename)

    #     # # Remove from graph:
    #     # # Delete with neomodel the dataobject
    #     # try:
    #     #     dataobj_node.delete()
    #     # except graph.DigitalEntity.DoesNotExist:
    #     #     return self.force_response(errors={uuid: 'Not found.'})

    #     # # Delete collection if not linked to any dataobject anymore?
    #     # if len(collection_node.belongs.all()) < 1:
    #     #     collection_node.delete()

    #     # Remove from irods
    #     icom.remove(ipath)
    #     logger.info("Removed %s", ipath)

    #     return self.force_response({'deleted': ipath})
