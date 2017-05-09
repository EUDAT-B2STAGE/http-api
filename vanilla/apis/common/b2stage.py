# -*- coding: utf-8 -*-

"""
Common functions for EUDAT endpoints
"""

import os
import re
from rapydo.rest.definition import EndpointResource
from eudat.apis.common import (
    CURRENT_HTTPAPI_SERVER, CURRENT_B2SAFE_SERVER,
    IRODS_PROTOCOL, HTTP_PROTOCOL,  # PRODUCTION,
    IRODS_VARS, InitObj
)
# from rapydo.confs import API_URL
from rapydo.utils.logs import get_logger

log = get_logger(__name__)


class EudatEndpoint(EndpointResource):
    """
        Extend normal API to init
        all necessary EUDAT B2STAGE API services
    """

    _r = None  # main resources handler
    _path_separator = '/'
    _post_delimiter = '?'
    _only_check_proxy = False

    def init_endpoint(self):

        # main object to handle token and oauth2 things
        user = self.get_current_user()
        intuser, extuser = self.auth.oauth_from_local(user)

        # If we have an "external user" we are using b2access oauth2
        # Var 'proxy' is referring to proxy certificate or normal certificate
        if extuser is None:
            # TODO: a more well thought user mapping
            # when not using B2ACCESS
            iuser = IRODS_VARS.get('guest_user')
            ipass = None
            # iuser = IRODS_VARS.get('user')
            # ipass = IRODS_VARS.get('password')

            proxy = False
        else:
            iuser = extuser.irodsuser
            ipass = None
            proxy = True

        icom = self.get_service_instance(
            service_name='irods',
            user=iuser, password=ipass, proxy=proxy)

        # Verify if irods certificates are ok
        try:
            # icd and ipwd do not give error with wrong certificates...
            # so the minimum command is ils inside the home dir
            icom.list()
            if self._only_check_proxy:
                return InitObj(is_proxy=proxy, valid_credentials=True)
        except BaseException as e:
            # Init the error and use it in above cases
            error = str(e)

            if self._only_check_proxy:
                if not IRODS_VARS.get('external'):
                    # TODO: enable automatic regeneration
                    log.critical("TO BE COMPLETED")
                    icom = self.get_service_instance('irods', be_admin=True)
                return InitObj(icommands=icom, is_proxy=proxy,
                               valid_credentials=False, extuser_object=extuser)

            if proxy:

                re1 = r':\s+(Error reading[^\:\n]+:[^\n]+\n[^\n]+)\n'
                re2 = r'proxy credential:\s+([^\s]+)\s+' \
                    + r'with subject:\s+([^\n]+)\s+' \
                    + r'expired\s+([0-9]+)\s+([^\s]+)\s+ago'

                pattern = re.compile(re1)
                mall = pattern.findall(error)
                if len(mall) > 0:
                    m = mall.pop()
                    return InitObj(
                        errors='Failed credentials: ' + m.replace('\n', ''))

                pattern = re.compile(re2)
                mall = pattern.findall(error)
                if len(mall) > 0:
                    m = mall.pop()
                    error = "'%s' became invalid %s %s ago. " \
                        % (m[1], m[2], m[3])
                    error += "To refresh the proxy make '%s' on URI '%s'" \
                        % ("POST", "/auth/proxy")
                    return InitObj(errors='Expired proxy credential: ' + error)

            return InitObj(errors=[error])

        # SQLALCHEMY connection
        sql = self.get_service_instance('sqlalchemy')
        user = intuser.email

        #####################################
        log.very_verbose("Base obj [i{%s}, s{%s}, u {%s}]" % (icom, sql, user))
        return InitObj(
            username=user,
            extuser_object=extuser,
            icommands=icom,
            db_handler=sql,
            is_proxy=proxy
        )

    def httpapi_location(self, ipath, api_path=None, remove_suffix=None):
        """ URI for retrieving with GET method """

        # TODO: check and clean 'remove_suffix parameter'

        # if remove_suffix is not None and uri_path.endswith(remove_suffix):
        #     uri_path = uri_path.replace(remove_suffix, '')

        if api_path is None:
            api_path = ''
        else:
            api_path = "/%s" % api_path.lstrip('/')

        return '%s://%s%s/%s' % (
            HTTP_PROTOCOL, CURRENT_HTTPAPI_SERVER, api_path,
            ipath.strip(self._path_separator))

    def b2safe_location(self, ipath):
        return '%s:///%s/%s' % (
            IRODS_PROTOCOL, CURRENT_B2SAFE_SERVER,
            ipath.strip(self._path_separator))

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
        # log.pp(myargs)

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

        force = myargs.get('force')
        """ Works with:
           http POST $SERVER/api/namespace path=/path/to/dir force:=1 "$AUTH"
           http POST $SERVER/api/namespace path=/path/to/dir force=True "$AUTH"
           http POST $SERVER/api/namespace path=/path/to/dir force=true "$AUTH"
        """
        if force is None:
            force = False
        else:
            if isinstance(force, str):
                if force.lower() == 'true':
                    force = True
                else:
                    force = False
            elif isinstance(force, int):
                force = (force == 1)

        ############################
        log.verbose(
            "Parameters [file{%s}, path{%s}, res{%s}, force{%s}]"
            % (filename, path, resource, force))
        return path, resource, filename, force

    def download_object(self, r, path):
        icom = r.icommands
        username = r.username
        path, resource, filename, force = \
                    self.get_file_parameters(icom, path=path)
        is_collection = icom.is_collection(path)
        if is_collection:
            return self.send_errors(
                'Collection: recursive download is not allowed')

        if filename is None:
                filename=self.filename_from_path(path)
        abs_file=self.absolute_upload_file(filename, username)

        # TODO: decide if we want to use a cache when streaming
        # what about nginx caching?

        # Make sure you remove any cached version to get a fresh obj
        try:
            os.remove(abs_file)
        except:
            pass
        # Execute icommand (transfer data to cache)
        icom.open(path, abs_file)
        # Download the file from local fs
        filecontent=self.download(
            filename, subfolder=username, get=True)
        # Remove local file
        os.remove(abs_file)
        # Stream file content
        return filecontent