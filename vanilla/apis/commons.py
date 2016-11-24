# -*- coding: utf-8 -*-

"""
Common functions for EUDAT endpoints
"""

from __future__ import absolute_import

import os
from attr import (
    s as AttributedModel,
    ib as attribute,
)
from ..base import ExtendedApiResource
from commons.logs import get_logger
from ..services.irods.client import IRODS_DEFAULT_USER

logger = get_logger(__name__)


########################
#  A class with attributes
########################
@AttributedModel
class InitObj(object):
    """
    A pythonic way to handle a method response with different features
    """

    # User info
    username = attribute(default=None)
    extuser_object = attribute(default=None)
    # Service handlers
    icommands = attribute(default=None)
    db_handler = attribute(default=None)
    # Verify certificates or normal credentials
    is_proxy = attribute(default=False)
    valid_credentials = attribute(default=False)
    # Save errors to report
    errors = attribute(default=None)


########################
#  Extend normal API to init EUDAT B2STAGE API services
########################

class EudatEndpoint(ExtendedApiResource):

    _path_separator = '/'

    def init_endpoint(self, only_check_proxy=False):

        # main object to handle token and oauth2 things
        auth = self.global_get('custom_auth')

        # Get the irods user
        # (either from oauth or using default)
        iuser = IRODS_DEFAULT_USER
        use_proxy = False
        intuser, extuser = auth.oauth_from_local(self.get_current_user())
        # If we have an "external user" we are using b2access oauth2
        if extuser is not None:
            iuser = extuser.irodsuser
            use_proxy = True
        icom = self.global_get_service('irods', user=iuser, proxy=use_proxy)

        # Verify if irods certificates are ok
        try:
            # icd and ipwd do not give error with wrong certificates...
            # so the minimum command is ils inside the home dir
            icom.list()
            if only_check_proxy:
                return InitObj(is_proxy=use_proxy, valid_credentials=True)
        except Exception as e:
            if only_check_proxy:
                return InitObj(is_proxy=use_proxy,
                               valid_credentials=False, extuser_object=extuser)

            if use_proxy:
                import re
                error = str(e)

                re1 = r':\s+(Error reading[^\:\n]+:[^\n]+\n[^\n]+)\n'
                re2 = r'proxy credential:\s+([^\s]+)\s+' \
                    + r'with subject:\s+([^\n]+)\s+' \
                    + r'expired\s+([0-9]+)\s+([^\s]+)\s+ago'

                pattern = re.compile(re1)
                mall = pattern.findall(error)
                if len(mall) > 0:
                    m = mall.pop()
                    return InitObj(
                        errors={'Failed credentials': m.replace('\n', '')})

                pattern = re.compile(re2)
                mall = pattern.findall(error)
                if len(mall) > 0:
                    m = mall.pop()
                    error = "'%s' became invalid %s %s ago. " \
                        % (m[1], m[2], m[3])
                    error += "To refresh the proxy make '%s' on URI '%s'" \
                        % ("POST", "/auth/proxy")
                    return InitObj(
                        errors={'Expired proxy credential': error})

            return InitObj(
                errors={'Invalid proxy credential': error})

        # SQLALCHEMY connection
        sql = self.global_get_service('sql')
        user = intuser.email

        #####################################
        logger.debug("Base obj [i{%s}, s{%s}, u {%s}]" % (icom, sql, user))
        return InitObj(
            username=user,
            extuser_object=extuser,
            icommands=icom,
            db_handler=sql,
            is_proxy=use_proxy
        )

    def fix_location(self, irods_location):
        if not irods_location.startswith(self._path_separator):
            irods_location = self._path_separator + irods_location
        return irods_location

    @staticmethod
    def username_from_unity(unity_persistent):
        """ Take the last piece of the unity id """
        return unity_persistent.split('-')[::-1][0]

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

    def get_file_parameters(self, icom,
                            path=None, filename=None, newfile=False):
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
        if newfile:
            filename = myargs.get('newname')

        resource = myargs.get('resource')
        # if resource is None:
        #     resource = icom.get_default_resource()

        force = self._args.get('force')

        ############################
        logger.debug(
            "Parameters [file{%s}, path{%s}, res{%s}, force{%s}]"
            % (filename, path, resource, force))
        return path, resource, filename, force
