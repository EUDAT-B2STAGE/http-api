# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from restapi import get_logger
from ..base import ExtendedApiResource
from .. import decorators as decorate

# Security
# from confs import config
# from flask.ext.security import roles_required, auth_token_required

logger = get_logger(__name__)


#####################################
class JustATest(ExtendedApiResource):

    @decorate.apimethod
    def get(self):
        logger.warning("a call")
        return self.response('Hello world!')


# #####################################
# from ..services.neo4j.graph import GraphFarm
# class GraphTest(ExtendedApiResource, GraphFarm):

#     @decorate.apimethod
#     def get(self):
#         graph = self.get_graph_instance()
#         print(graph)
#         logger.warning("a call")
#         return self.response('Hello world!')
