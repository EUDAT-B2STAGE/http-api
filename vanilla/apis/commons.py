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
        for key, value in myargs.items():
            if value is None:
                del myargs[key]
        from beeprint import pp
        pp(myargs)

        ############################
        # main parameters

## TO FIX
# path (zone + collection path) and filename are coupled together
        # if filename is None:
        #     tmp = myargs.get('filename')
        #     if tmp is not None:
        #         filename = tmp

        print("PATH 0", path)
        if path is None:
            path = myargs.get('path', icom.get_user_home(iuser))
            print("PATH 1", path)
        print("PATH 2", path)
        filename = self.filename_from_path(path)
        pp(self.splitall(path))

        # https://docs.python.org/3/library/os.path.html
        # os.path.isabs(path)
        # os.path.isfile(path)

        resource = myargs.get('resource')
        # if resource is None:
        #     resource = icom.get_default_resource()

        ############################
        logger.debug(
            "Parameters [f{%s}, p{%s}, r{%s}]" % (filename, path, resource))
        return path, resource, filename
