# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from rapydo.rest.definition import EndpointResource
from rapydo.services.detect import detector

from rapydo.utils.logs import get_logger

log = get_logger(__name__)


#####################################
class JustATest(EndpointResource):

    def get(self):
        log.warning("Received a test HTTP request")
        return self.force_response('Hello world!')


#####################################
# if SQL_AVAILABLE:
if detector.check_availability('sqlalchemy'):

    class SqlEndPoint(EndpointResource):

        def get(self):
            sql = self.global_get_service('sql')
            print(sql)
            log.warning("a call")
            return self.force_response('Hello world!')


#####################################
# if GRAPHDB_AVAILABLE:
if detector.check_availability('neo4j'):

    class GraphEndPoint(EndpointResource):

        def get(self):

            user = self.get_current_user()
            graph = self.global_get_service('neo4j')
            print(graph)
            log.warning("a call")
            return self.force_response('Hello world, %s!' % user)
