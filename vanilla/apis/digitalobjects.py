# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
"""

from __future__ import absolute_import

import os
# from commons import htmlcodes as hcodes
from commons.logs import get_logger
from ..base import ExtendedApiResource
from ..services.irods.client import IrodsException, IRODS_DEFAULT_USER
from ..services.uploader import Uploader
# from ..services.irods.translations import DataObjectToGraph
from .. import decorators as decorate
from ...auth import authentication
# from ...confs import config

logger = get_logger(__name__)

## // TO FIX:
# Use the correct irods user from the token,
# instad of IRODS_DEFAULT_USER
irods_tmp_user = IRODS_DEFAULT_USER


###############################
# Classes


class CollectionEndpoint(ExtendedApiResource):
    """
    This endpoint does not exist anymore.
    It is referred as DigitalObject or Aggregation,
    which are graph Nodes but we do not have a dedicated endpoint
    """

    pass

#     @authentication.authorization_required
#     @decorate.apimethod
#     @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
#     def get(self, uuid=None):
#         """
#         Return list of elements inside a collection.
#         If uuid is added, get the single element.
#         """

#         graph = self.global_get_service('neo4j')

#     ##########
# ## // TO FIX!!
# # List collections and dataobjects only linked to current user :)

#         # auth = self.global_get('custom_auth')
#         # graph_user = auth.get_user_object(payload=auth._payload)
#         # # get the irods_user connected to graph_user
#         # icom = self.global_get_service('irods', user=FIND_THE_USER)
#     ##########

#         content = []

#         # Get ALL elements
#         if uuid is None:
#             content = graph.Collection.nodes.all()
#         # Get SINGLE element
#         else:
#             try:
#                 content.append(graph.Collection.nodes.get(id=uuid))
#             except graph.Collection.DoesNotExist:
#                 return self.force_response(errors={uuid: 'Not found.'})

#         # Build jsonapi.org compliant response
#         data = self.formatJsonResponse(content)
#         return self.force_response(data)

# ###############
# ## // TO DO:
# # The one above is such a standard 'get' method that
# # we could make it general for the graphdb use case
# ###############

#     @authentication.authorization_required
#     @decorate.add_endpoint_parameter('collection', required=True)
#     @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
#     @decorate.apimethod
#     @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
#     def post(self):
#         """ Create one collection/directory """

#         icom = self.global_get_service('irods', user=irods_tmp_user)
#         collection_input = self._args.get('collection')
#         ipath = icom.create_empty(
#             collection_input,
#             directory=True, ignore_existing=self._args.get('force'))
#         logger.info("Created irods collection: %s", ipath)

#         # Save inside the graph and give back the uuid
#         translate = DataObjectToGraph(
#             icom=icom, graph=self.global_get_service('neo4j'))
#         _, collections, zone = translate.split_ipath(ipath, with_file=False)
#         node = translate.recursive_collection2node(
#             collections, current_zone=zone)

#         return self.force_response(
#             {'id': node.id, 'collection': ipath},
#             code=hcodes.HTTP_OK_CREATED)

#     @authentication.authorization_required
#     @decorate.add_endpoint_parameter('collection', required=False)
#     @decorate.apimethod
#     @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
#     def delete(self, uuid):
#         """ Remove an object """

#         # Get the dataobject from the graph
#         graph = self.global_get_service('neo4j')
#         node = None
#         try:
#             node = graph.Collection.nodes.get(id=uuid)
#         except graph.Collection.DoesNotExist:
#             return self.force_response(errors={uuid: 'Not found.'})

#         icom = self.global_get_service('irods', user=irods_tmp_user)
#         ipath = icom.handle_collection_path(node.path)

#         # Remove from graph:
#         node.delete()
#         # Remove from irods
#         icom.remove(ipath, recursive=True)
#         logger.info("Removed collection %s", ipath)

#         return self.force_response({'deleted': ipath})


class EntitiesEndpoint(Uploader, ExtendedApiResource):

    @authentication.authorization_required
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self, doid=None, eid=None):
        """
        Download file from eid
        """
        if doid is None and eid is None:
            return self.method_not_allowed()

    #     graph = self.global_get_service('neo4j')

    #     # Getting the list
    #     if uuid is None:
    #         data = self.formatJsonResponse(graph.DigitalEntity.nodes.all())
    #         return self.force_response(data)

    #     # # If trying to use a path as file
    #     # elif name[-1] == '/':
    #     #     return self.force_response(
    #     #         errors={'dataobject': 'No dataobject/file requested'})

    #     # Do irods things
    #     icom = self.global_get_service('irods', user=irods_tmp_user)
    #     user = icom.get_current_user()

    #     # Get filename and ipath from uuid using the graph
    #     try:
    #         dataobj_node = graph.DigitalEntity.nodes.get(id=uuid)
    #     except graph.DigitalEntity.DoesNotExist:
    #         return self.force_response(errors={uuid: 'Not found.'})
    #     collection_node = dataobj_node.belonging.all().pop()

    #     # irods paths
    #     ipath = icom.get_irods_path(
    #         collection_node.path, dataobj_node.filename)

    #     abs_file = self.absolute_upload_file(dataobj_node.filename, user)
    #     # Make sure you remove any cached version to get a fresh obj
    #     try:
    #         os.remove(abs_file)
    #     except:
    #         pass

    #     # Execute icommand (transfer data to cache)
    #     icom.open(ipath, abs_file)

    #     # Download the file from local fs
    #     filecontent = super().download(
    #         dataobj_node.filename, subfolder=user, get=True)

    #     # Remove local file
    #     os.remove(abs_file)

    #     # Stream file content
    #     return filecontent

    @authentication.authorization_required
    # @decorate.add_endpoint_parameter('collection')
    @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def post(self):
        """
        Handle file upload
        http --form POST localhost:8080/api/dataobjects \
            file@docker-compose.test.yml
        """

        # if SOMETHING:
        #     return self.method_not_allowed()

        return "TO DO!"

    #     icom = self.global_get_service('irods', user=irods_tmp_user)
    #     user = icom.get_current_user()

    #     # Original upload
    #     response = super(DigitalEntityEndpoint, self).upload(subfolder=user)

    #     # If response is success, save inside the database
    #     key_file = 'filename'
    #     filename = None

    #     content = self.get_content_from_response(response)
    #     errors = self.get_content_from_response(response, get_error=True)
    #     status = self.get_content_from_response(response, get_status=True)

    #     if isinstance(content, dict) and key_file in content:
    #         filename = content[key_file]
    #         abs_file = self.absolute_upload_file(filename, user)
    #         logger.info("File is '%s'" % abs_file)

    #         ############################
    #         # Move file inside irods

    #         # ##HANDLING PATH
    #         # The home dir for the current user
    #         # Where to put the file in irods
    #         ipath = icom.get_irods_path(
    #             self._args.get('collection'), filename)

    #         try:
    #             iout = icom.save(
    #                 abs_file, destination=ipath, force=self._args.get('force'))
    #             logger.info("irods call %s", iout)
    #         finally:
    #             # Remove local cache in any case
    #             os.remove(abs_file)

    #         # ######################
    #         # # Save into graphdb
    #         # graph = self.global_get_service('neo4j')

    #         # translate = DataObjectToGraph(graph=graph, icom=icom)
    #         # uuid = translate.ifile2nodes(
    #         #     ipath, service_user=self.global_get('custom_auth')._user)

    #         uuid = None

    #         # Create response
    #         content = {
    #             'collection': ipath,
    #             'id': uuid
    #         }

    #     # Reply to user
    #     return self.force_response(content, errors=errors, code=status)

    # @authentication.authorization_required
    # @decorate.apimethod
    # @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    # def delete(self, uuid):
    #     """ Remove an object """

    #     # Get the dataobject from the graph
    #     graph = self.global_get_service('neo4j')
    #     dataobj_node = graph.DigitalEntity.nodes.get(id=uuid)
    #     collection_node = dataobj_node.belonging.all().pop()

    #     icom = self.global_get_service('irods', user=irods_tmp_user)
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


class DigitalObjectsEndpoint(ExtendedApiResource):

    @authentication.authorization_required
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self, doid=None):
        """
        Get object from ID
        """

        return "TO DO!"
