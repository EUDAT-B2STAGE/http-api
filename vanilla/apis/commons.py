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

        icom = self.global_get_service('irods', user=user)

        return icom, sql, user
