# -*- coding: utf-8 -*-

"""
Common functions for EUDAT endpoints
"""

from __future__ import absolute_import

import os
import sys
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

    @staticmethod
    def splitall(path):
        allparts = []
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path:  # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        return allparts

    @staticmethod
    def filename_from_path(path):
        return os.path.basename(os.path.normpath(path))

    def get_file_parameters(self, icom, path=None):
        """
        Note: the resource is a complicated parameter.
        Resources are meant for (iRODS) replicas.
        Adding or removing replicas require explicit irods commands.
        """

        iuser = icom.get_current_user()

        ############################
        # Handle flask differences on GET/DELETE with PUT/POST
        myargs = self.get_input()

        ############################
        # main parameters

        filename = None

        # If empty the first time, we received path from the URI
        if path is None:
            path = myargs.get('path')
        # If path is empty again, I rely to the home of the user
        if path is None:
            path = icom.get_user_home(iuser)
        elif not os.path.isabs(path):
            path = icom.get_user_home(iuser) + '/' + path

        # # Should this check be done to uploaded file?
        # if os.path.isfile(path):
        #     filename = self.filename_from_path(path)

        resource = myargs.get('resource')
        # if resource is None:
        #     resource = icom.get_default_resource()

        ############################
        logger.debug(
            "Parameters [f{%s}, p{%s}, r{%s}]" % (filename, path, resource))
        return path, resource, filename
