# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from ... import get_logger
from ..base import ExtendedApiResource
from .. import decorators as decorate
from ..services.detect import SQL_AVAILABLE, GRAPHDB_AVAILABLE
from ...auth import auth

logger = get_logger(__name__)


#####################################
class JustATest(ExtendedApiResource):

    @decorate.apimethod
    def get(self):
        logger.warning("a call")
        return self.response('Hello world!')


#####################################
if SQL_AVAILABLE:

    class SqlEndPoint(ExtendedApiResource):

        @auth.login_required
        @decorate.apimethod
        def get(self):
            sql = self.global_get_service('sql')
            print(sql)
            logger.warning("a call")
            return self.response('Hello world!')


#####################################
if GRAPHDB_AVAILABLE:

    class GraphEndPoint(ExtendedApiResource):

        @auth.login_required
        @decorate.apimethod
        def get(self):
            graph = self.global_get_service('neo4j')
            print(graph)
            logger.warning("a call")
            return self.response('Hello world!')
