# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.

A digital object is
...

"""

# from commons import htmlcodes as hcodes
from ..base import ExtendedApiResource
from ..services.irods.client import IrodsException
# from ..services.irods.translations import Irods2Graph
from .. import decorators as decorate
from ...auth import authentication
# from ...confs import config
from commons.logs import get_logger

log = get_logger(__name__)


###############################
# Classes

class DigitalObjectsEndpoint(ExtendedApiResource):

    @authentication.authorization_required
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, doid=None):
        """
        Get object from ID
        """

        return "TO DO!"

    @authentication.authorization_required
    # @decorate.add_endpoint_parameter('user')
    # @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def post(self):
        """
        Create an id for the digital object
        """

        user = self._args.get('user', None)
        if user is not None:
            userobj = None
            raise NotImplementedError("Must recover the graph obj from user")
        else:
            userobj = self.get_current_user()

        graph = self.global_get_service('neo4j')
        # icom = self.global_get_service('irods')
        uuid = self._post(graph, userobj)

        # Reply to user
        return self.force_response(uuid)  # , errors=errors, code=status)

    def _post(self, graph, user, location=None):

## WORK IN PROGRESS

        # Make DOID from location
        from commons.services.uuid import getUUIDfromString
        if location is None:
            import datetime
            now = datetime.datetime.now().isoformat()
            pattern = "noprotocol://%s/%s/%s" \
                % (user.surname, user.name, now)
        else:
            pattern = location
        doid = getUUIDfromString(pattern)
        print("pattern", pattern, doid)

        # Create the dataobject...
        graph.DigitalEntity(_id=doid, location=location)

        # If location, do some collection/aggregations/resource/zone things
        # and connect them

        # Link object to user

        """
            # translate = DataObjectToGraph(graph=graph, icom=icom)
            # uuid = translate.ifile2nodes(
            #     ipath, service_user=self.global_get('custom_auth')._user)
        """

        return 'TO DO'

    # @authentication.authorization_required
    # @decorate.apimethod
    # @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    # def delete(self, uuid):
    #     """ Remove DO """


class CollectionEndpoint(ExtendedApiResource):
    """
    This endpoint does not exist anymore.
    It is referred as: DigitalEntity or DigitalObject or Aggregation,
    which are graph Nodes, but we do not have a dedicated endpoint.
    """

    pass

#     @authentication.authorization_required
#     @decorate.apimethod
#     @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
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
#     @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
#     def post(self):
#         """ Create one collection/directory """

#         icom = self.global_get_service('irods')
#         collection_input = self._args.get('collection')
#         ipath = icom.create_empty(
#             collection_input,
#             directory=True, ignore_existing=self._args.get('force'))
#         log.info("Created irods collection: %s", ipath)

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
#     @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
#     def delete(self, uuid):
#         """ Remove an object """

#         # Get the dataobject from the graph
#         graph = self.global_get_service('neo4j')
#         node = None
#         try:
#             node = graph.Collection.nodes.get(id=uuid)
#         except graph.Collection.DoesNotExist:
#             return self.force_response(errors={uuid: 'Not found.'})

#         icom = self.global_get_service('irods')
#         ipath = icom.handle_collection_path(node.path)

#         # Remove from graph:
#         node.delete()
#         # Remove from irods
#         icom.remove(ipath, recursive=True)
#         log.info("Removed collection %s", ipath)

#         return self.force_response({'deleted': ipath})
