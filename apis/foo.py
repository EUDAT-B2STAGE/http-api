# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from rapydo.rest.definition import EndpointResource
from rapydo.services.detect import SQL_AVAILABLE, GRAPHDB_AVAILABLE

from rapydo.utils.logs import get_logger

logger = get_logger(__name__)


#####################################
class JustATest(EndpointResource):

    def get(self):
        logger.warning("Received a test HTTP request")
        return self.force_response('Hello world!')


#####################################
if SQL_AVAILABLE:

    class SqlEndPoint(EndpointResource):

        def get(self):
            sql = self.global_get_service('sql')
            print(sql)
            logger.warning("a call")
            return self.force_response('Hello world!')


#####################################
if GRAPHDB_AVAILABLE:

    class GraphEndPoint(EndpointResource):

        def get(self):

            user = self.get_current_user()
            graph = self.global_get_service('neo4j')
            print(graph)
            logger.warning("a call")
            return self.force_response('Hello world, %s!' % user)
