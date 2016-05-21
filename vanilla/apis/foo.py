# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from ... import get_logger, htmlcodes as hcodes
from ..base import ExtendedApiResource
from .. import decorators as decorate
from ..services.detect import GRAPHDB_AVAILABLE
from ..services.neo4j.graph import GraphFarm

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


#####################################
if GRAPHDB_AVAILABLE:
    class GraphEndPoint(ExtendedApiResource, GraphFarm):

        @decorate.apimethod
        def get(self):
            graph = self.get_graph_instance()
            print(graph)
            logger.warning("a call")
            return self.response('Hello world!')
