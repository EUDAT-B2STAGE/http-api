# -*- coding: utf-8 -*-

"""
Common functions for EUDAT endpoints
"""

from __future__ import absolute_import

from ..base import ExtendedApiResource
from commons.logs import get_logger

logger = get_logger(__name__)


class EudatEndpoint(ExtendedApiResource):

    def init_endpoint(self):

        #####################################
        # IF THE GRAPH WILL BE INTEGRATED

        # # Note: graph holds the authenticated accounts in our architecture
        # graph = self.global_get_service('neo4j')
        # graphuser = self.get_current_user()
        # irodsuser = icom.translate_graph_user(graph, graphuser)
        # icom = self.global_get_service('irods', user=irodsuser.username)
        #####################################

        sql = self.global_get_service('sql')

        #####################################
        # OTHERWISE
        # Get current (irods?) user from database/tokens
# // TO FIX:
        user = 'guest'
        # user = 'rodsminer'

        icom = self.global_get_service('irods', user=user)
        logger.debug("Base obj [i{%s}, s{%s}, u {%s}]" % (icom, sql, user))
        return icom, sql, user

    def get_file_parameters(self, icom, filename=None):
        iuser = icom.get_current_user()
        path = self._args.get('path')
        if path is None:
            path = icom.get_user_home(iuser)
        resource = self._args.get('resource')
        if resource is None:
            resource = icom.get_default_resource()
        logger.debug(
            "Parameters [f{%s}, p{%s}, r{%s}]" % (filename, path, resource))
        return path, resource
