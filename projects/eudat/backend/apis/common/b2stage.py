# -*- coding: utf-8 -*-

"""
Common functions for EUDAT endpoints
"""

import os
# from restapi.rest.definition import EndpointResource
from restapi.exceptions import RestApiException
from eudat.apis.common.b2access import B2accessUtilities
from eudat.apis.common import (
    CURRENT_HTTPAPI_SERVER, CURRENT_B2SAFE_SERVER,
    IRODS_PROTOCOL, HTTP_PROTOCOL, PRODUCTION,
    IRODS_VARS, InitObj
)
# from restapi.confs import API_URL
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


# class EudatEndpoint(EndpointResource):
class EudatEndpoint(B2accessUtilities):
    """
        Extend normal API to init
        all necessary EUDAT B2STAGE API services
    """

    _r = None  # main resources handler
    _path_separator = '/'
    _post_delimiter = '?'

    def init_endpoint(self):

        # Get user information from db, associated to token
        # NOTE: user legenda
        # internal_user = user internal to the API
        # external_user = user from oauth (B2ACCESS)
        internal_user = self.get_current_user()
        log.debug("Token user: %s" % internal_user)

        #################################
        # decide which type of auth we are dealing with
        # NOTE: icom = irods commands handler (official python driver PRC)

        proxy = False
        external_user = None
        if internal_user.authmethod == 'credentials':
            icom = self.irodsuser_from_b2stage(internal_user)
        elif internal_user.authmethod == 'irods':
            icom = self.irodsuser_from_b2safe(internal_user)
        elif internal_user.authmethod == 'oauth2':
            icom, external_user, proxy = \
                self.irodsuser_from_b2access(internal_user)
        else:
            log.exit("Unknown credentials provided")

        #################################
        # Verify if irods certificates are ok
        refreshed = False
        try:
            # icd and ipwd do not give error with wrong certificates...
            # so the minimum command is ils inside the home dir
            icom.list()
            # TODO: doublecheck if list is the best option with PRC

            if proxy:
                log.debug("Current proxy certificate is valid")

        # Catch exceptions on this irods test
        # To manipulate the reply to be given to the user
        except BaseException as e:
            log.warning("Catched exception %s" % type(e))

            if proxy:
                error = self.check_proxy_certificate(external_user, e)
                if error is None:
                    refreshed = True
                else:
                    # Case of error to be printed
                    return self.parse_gss_failure(error)
            else:
                raise e

        #################################
        # database connection
        sql = self.get_service_instance('sqlalchemy')
        # update user variable to account email, which should be always unique
        user = internal_user.email

        #####################################
        log.very_verbose(
            "Base objects for current requets [i{%s}, s{%s}, u {%s}]"
            % (icom, sql, user))

        return InitObj(
            username=user, extuser_object=external_user,
            icommands=icom, db_handler=sql,
            valid_credentials=True, is_proxy=proxy, refreshed=refreshed
        )

    def irodsuser_from_b2access(self, internal_user):
        """ Certificates X509 and authority delegation """
        proxy = True
        external_user = self.auth.oauth_from_local(internal_user)

        return \
            self.get_service_instance(
                service_name='irods', only_check_proxy=True,
                user=external_user.irodsuser, password=None,
                gss=proxy, proxy_file=external_user.proxyfile,
            ), \
            external_user, \
            proxy

    def irodsuser_from_b2safe(self, user):

        if user.session is not None and len(user.session) > 0:
            log.debug("Validated B2SAFE user: %s" % user.uuid)
        else:
            msg = "Current credentials not registered inside B2SAFE"
            raise RestApiException(
                msg, status_code=hcodes.HTTP_BAD_UNAUTHORIZED)

        return self.get_service_instance(
            service_name='irods', user_session=user)

    def irodsuser_from_b2stage(self, internal_user):
        """
        Normal credentials (only available inside the HTTP API database)
        aren't mapped to a real B2SAFE user.
        We force the guest user if it's indicated in the configuration.
        This usecase has to be avoided in production.
        """

        if PRODUCTION:
            raise ValueError("Invalid authentication")

        # NOTE: this 'guest' irods mode is only for debugging purpose
        return self.get_service_instance(
            service_name='irods', only_check_proxy=True,
            user=IRODS_VARS.get('guest_user'), password=None, gss=True,
        )

    def parse_gss_failure(self, error_object):

        errors = error_object.errors.copy()

        for error in errors:

            log.warning("GSS failure:\n%s" % error)

            if 'GSS failure' in error or \
               ('Invalid credential' in error and ' GSS ' in error):

                import re
                new_error = None

                if "Unable to verify remote side's credentials" in error:
                    regexp = r'OpenSSL Error:.+:([^\n]+)'
                    pattern = re.compile(regexp)
                    match = pattern.search(error)
                    new_error = 'B2ACCESS proxy not trusted by B2SAFE'
                    if match:
                        new_error += ': ' + match.group(1).strip()

                # globus_sysconfig: Error with certificate filename
                elif 'Error with certificate filename' in error:

                    regexp = r'globus_[^\:]+:([^\n]+)'
                    pattern = re.compile(regexp)
                    matches = pattern.findall(error)

                    if matches:
                        print(matches)
                        last_error = matches.pop()
                        if 'is not a valid file' in last_error:
                            if 'File does not exist' in last_error:
                                new_error = 'B2ACCESS proxy file not found'
                            else:
                                new_error = 'B2ACCESS proxy file invalid'

                if new_error is not None:
                    error_object.errors = [new_error]

        return error_object

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
        return '%s://%s/%s' % (
            IRODS_PROTOCOL, CURRENT_B2SAFE_SERVER,
            ipath.strip(self._path_separator))

    def fix_location(self, irods_location):
        if not irods_location.startswith(self._path_separator):
            irods_location = self._path_separator + irods_location
        return irods_location

    # @staticmethod
    # def user_from_unity(unity_persistent):
    #     """ Take the last piece of the unity id """
    #     return unity_persistent.split('-')[::-1][0]

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
        if filename is not None:
            path += '/' + filename.rstrip('/')
        return path

    def get_file_parameters(self, icom,
                            path=None, filename=None, newfile=False):
        """
        NOTE: resource is a complicated parameter:
        resources are meant for (iRODS) replicas;
        adding or removing replicas require explicit irods commands.
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

        if isinstance(path, str):
            path = path.rstrip(self._path_separator)

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
            filename = self.filename_from_path(path)
        abs_file = self.absolute_upload_file(filename, username)

        # TODO: decide if we want to use a cache when streaming
        # what about nginx caching?

        # Make sure you remove any cached version to get a fresh obj
        try:
            os.remove(abs_file)
        except BaseException:
            pass
        # Execute icommand (transfer data to cache)
        icom.open(path, abs_file)
        # Download the file from local fs
        filecontent = self.download(filename, subfolder=username, get=True)
        # Remove local file
        os.remove(abs_file)
        # Stream file content
        return filecontent
