# -*- coding: utf-8 -*-

"""
Common functions for EUDAT endpoints
"""

from __future__ import absolute_import

import os
from ..base import ExtendedApiResource
from commons.logs import get_logger
from ..services.irods.client import IRODS_DEFAULT_USER

logger = get_logger(__name__)


class EudatEndpoint(ExtendedApiResource):

    def init_endpoint(self, only_check_proxy=False):

        # main object to handle token and oauth2 things
        auth = self.global_get('custom_auth')

        # Get the irods user
        # (either from oauth or using default)
        iuser = IRODS_DEFAULT_USER
        use_proxy = False
        intuser, extuser = auth.oauth_from_local(self.get_current_user())
        if extuser is not None:
            iuser = extuser.irodsuser
            use_proxy = True
        icom = self.global_get_service('irods', user=iuser, proxy=use_proxy)

        regexp = r'The proxy credential:\s+([^\s]+)\s+' \
            + r'with subject:\s+([^\s]+)\s+expired\s+([0-9]+)\s+([^\s]+)\s+ago'

        # Verify if irods certificates are ok
        try:
            # icd and ipwd do not give error with wrong certificates...
            # so the minimum command is ils inside the home dir
            icom.list()
            if only_check_proxy:
                return True
        except Exception as e:
            if only_check_proxy:
                return False
            import re
            pattern = re.compile(regexp)
            mall = pattern.findall(str(e))
            if len(mall) > 0:
                m = mall.pop()
                error = "'%s' became invalid %s %s ago" % (m[1], m[2], m[3])
                return self.send_errors('Expired proxy credential', error)
            else:
                raise e

        # SQLALCHEMY connection
        sql = self.global_get_service('sql')
        user = intuser.email

        #####################################
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

    def complete_path(self, path, filename=None):
        """ Make sure you have a path with no trailing slash """
        path = path.rstrip('/')
        # print("PATH 1", path)
        if filename is not None:
            path += '/' + filename.rstrip('/')
        # print("PATH 2", path)
        return path

    def get_file_parameters(self, icom, path=None, filename=None):
        """
        Note: the resource is a complicated parameter.
        Resources are meant for (iRODS) replicas.
        Adding or removing replicas require explicit irods commands.
        """

        # iuser = icom.get_current_user()

        ############################
        # Handle flask differences on GET/DELETE and PUT/POST
        myargs = self.get_input()

        ############################
        # main parameters

        # If empty the first time, we received path from the URI
        if path is None:
            # path = icom.get_user_home(iuser)
            path = myargs.get('path')

        # If path is empty again or we have a relative path, send empty
        # so that we can give an error
        if path is None or not os.path.isabs(path):
            return [None] * 4

        ############################

        filename = None

        # # Should this check be done to uploaded file?
        # if os.path.isfile(path):
        #     filename = self.filename_from_path(path)

        resource = myargs.get('resource')
        # if resource is None:
        #     resource = icom.get_default_resource()

        # This argument is used only for POST / PUT
        force = self._args.get('force')

        ############################
        logger.debug(
            "Parameters [file{%s}, path{%s}, res{%s}, force{%s}]"
            % (filename, path, resource, force))
        return path, resource, filename, force
