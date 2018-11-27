# -*- coding: utf-8 -*-

"""
Common functions for EUDAT endpoints
"""

import os
from irods import exception as iexceptions
# from restapi.rest.definition import EndpointResource
from restapi.exceptions import RestApiException
from b2stage.apis.commons.b2access import B2accessUtilities
from b2stage.apis.commons import (
    CURRENT_HTTPAPI_SERVER, CURRENT_B2SAFE_SERVER,
    IRODS_PROTOCOL, HTTP_PROTOCOL, PRODUCTION,
    IRODS_VARS, InitObj
)
# from restapi.confs import API_URL
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)

MISSING_BATCH = 0
NOT_FILLED_BATCH = 1
PARTIALLY_ENABLED_BATCH = 2
ENABLED_BATCH = 3
BATCH_MISCONFIGURATION = 4


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
        # VERIFY FOR SEADATA
        # print("TEST", internal_user)
        log.debug("Token user: %s" % internal_user)

        #################################
        # decide which type of auth we are dealing with
        # NOTE: icom = irods commands handler (official python driver PRC)

        proxy = False
        refreshed = False
        external_user = None

        if internal_user is None:
            raise AttributeError("Missing user association to token")

        if internal_user.authmethod == 'credentials':

            icom = self.irodsuser_from_b2stage(internal_user)

        elif internal_user.authmethod == 'irods':

            icom = self.irodsuser_from_b2safe(internal_user)

        elif internal_user.authmethod == 'b2access-cert':

            icom, external_user, refreshed, errors = \
                self.irodsuser_from_b2access_cert(internal_user)
            proxy = True
            if errors is not None:
                return errors

        elif internal_user.authmethod == 'b2access':
            icom, external_user, refreshed = \
                self.irodsuser_from_b2access(internal_user)
            # icd and ipwd do not give error with wrong certificates...
            # so the minimum command is ils inside the home dir
            icom.list()

        else:
            log.error("Unknown credentials provided")

        #################################
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

    def irodsuser_from_b2access(self, internal_user, refreshed=False):
        external_user = self.auth.oauth_from_local(internal_user)

        try:
            icom = self.get_service_instance(
                service_name='irods',
                user=external_user.irodsuser,
                password=external_user.token,
                authscheme='PAM'
            )

            log.debug("Current b2access token is valid")
        except iexceptions.PAM_AUTH_PASSWORD_FAILED:

            if external_user.refresh_token is None:
                log.warning(
                    "Missing refresh token cannot request for a new token")
                raise RestApiException('Invalid PAM credentials')
            else:

                if refreshed:
                    log.info("B2access token already refreshed, cannot request new one")
                    raise RestApiException('Invalid PAM credentials')
                log.info(
                    "B2access token is no longer valid, requesting new token")

                b2access = self.create_b2access_client(self.auth, decorate=True)
                access_token = self.refresh_b2access_token(
                    self.auth, external_user.email,
                    b2access, external_user.refresh_token)

                if access_token is not None:
                    return self.irodsuser_from_b2access(internal_user, refreshed=True)
                raise RestApiException('Failed to refresh b2access token')

        except BaseException as e:
            raise RestApiException(
                "Unexpected error: %s (%s)" % (type(e), str(e)))

        return icom, external_user, refreshed

    # B2access with certificates are no longer used
    def irodsuser_from_b2access_cert(self, internal_user):
        """ Certificates X509 and authority delegation """
        external_user = self.auth.oauth_from_local(internal_user)

        icom = self.get_service_instance(
            service_name='irods', only_check_proxy=True,
            user=external_user.irodsuser, password=None,
            gss=True, proxy_file=external_user.proxyfile,
        )

        refreshed = False
        try:
            # icd and ipwd do not give error with wrong credentials...
            # so the minimum command is ils inside the home dir
            icom.list()
            log.debug("Current proxy certificate is valid")

        # Catch exceptions on this irods test
        # To manipulate the reply to be given to the user
        except BaseException as e:
            log.warning("Catched exception %s" % type(e))

            error = self.check_proxy_certificate(external_user, e)
            if error is None:
                refreshed = True
            else:
                # Case of error to be printed
                return None, None, None, self.parse_gss_failure(error)

        return icom, external_user, refreshed, None

    def irodsuser_from_b2safe(self, user):

        if user.session is not None and len(user.session) > 0:
            log.debug("Validated B2SAFE user: %s" % user.uuid)
        else:
            msg = "Current credentials not registered inside B2SAFE"
            raise RestApiException(
                msg, status_code=hcodes.HTTP_BAD_UNAUTHORIZED)

        icom = self.get_service_instance(
            service_name='irods', user_session=user)

        return icom

    def irodsuser_from_b2stage(self, internal_user):
        """
        Normal credentials (only available inside the HTTP API database)
        aren't mapped to a real B2SAFE user.
        We force the guest user if it's indicated in the configuration.

        NOTE: this usecase is to be avoided in production.
        """

        if PRODUCTION:
            # 'guest' irods mode is only for debugging purpose
            raise ValueError("Invalid authentication")

        icom = self.get_service_instance(
            service_name='irods', only_check_proxy=True,
            user=IRODS_VARS.get('guest_user'), password=None, gss=True,
        )

        return icom

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

        # print("TEST", CURRENT_HTTPAPI_SERVER)

        return '%s://%s%s/%s' % (
            HTTP_PROTOCOL, CURRENT_HTTPAPI_SERVER, api_path,
            ipath.strip(self._path_separator))

    def b2safe_location(self, ipath):
        return '%s://%s/%s' % (
            IRODS_PROTOCOL, CURRENT_B2SAFE_SERVER,
            ipath.strip(self._path_separator))

    def fix_location(self, location):
        if not location.startswith(self._path_separator):
            location = self._path_separator + location
        return location

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
            "Parsed: file(%s), path(%s), res(%s), force(%s)",
            filename, path, resource, force)
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

    def download_parameter(self):
        # parse query parameters
        self.get_input()
        download = False
        if (hasattr(self._args, 'download')):
            if self._args.download and 'true' in self._args.download.lower():
                download = True
        return download

    def list_objects(self, icom, path, is_collection, location, public=False):
        """ DATA LISTING """

        from b2stage.apis.commons import CURRENT_MAIN_ENDPOINT, PUBLIC_ENDPOINT
        from restapi.flask_ext.flask_irods.client import IrodsException

        data = {}
        EMPTY_RESPONSE = {}

        #####################
        # DIRECTORY
        if is_collection:
            collection = path
            data = icom.list(path=collection)
            if len(data) < 1:
                data = EMPTY_RESPONSE
            # Print content list if it's a collection
        #####################
        # FILE (or not existing)
        else:
            collection = icom.get_collection_from_path(path)
            current_filename = path[len(collection) + 1:]

            from contextlib import suppress
            with suppress(IrodsException):
                filelist = icom.list(path=collection)
                data = EMPTY_RESPONSE
                for filename, metadata in filelist.items():
                    if filename == current_filename:
                        data[filename] = metadata
                # log.pp(data)

            # # Print file details/sys metadata if it's a specific file
            # data = icom.meta_sys_list(path)

            # if a path that does not exist
            if len(data) < 1:
                return self.send_errors(
                    "Path does not exists or you don't have privileges: %s"
                    % path, code=hcodes.HTTP_BAD_NOTFOUND)

        # Set the right context to each element
        response = []
        for filename, metadata in data.items():

            # Get iRODS checksum
            file_path = os.path.join(collection, filename)
            try:
                obj = icom.get_dataobject(file_path)
                checksum = obj.checksum
            except IrodsException:
                checksum = None

            # Get B2SAFE metadata
            out = {}
            try:
                out, _ = icom.get_metadata(file_path)
            except IrodsException:
                pass

            metadata['checksum'] = checksum
            metadata['PID'] = out.get("PID")

            # Shell we add B2SAFE metadata only if present?
            metadata['EUDAT/FIXED_CONTENT'] = out.get("EUDAT/FIXED_CONTENT")
            metadata['EUDAT/REPLICA'] = out.get("EUDAT/REPLICA")
            metadata['EUDAT/FIO'] = out.get("EUDAT/FIO")
            metadata['EUDAT/ROR'] = out.get("EUDAT/ROR")
            metadata['EUDAT/PARENT'] = out.get("EUDAT/PARENT")

            metadata.pop('path')
            if public:
                api_path = PUBLIC_ENDPOINT
            else:
                api_path = CURRENT_MAIN_ENDPOINT
            content = {
                'metadata': metadata,
                metadata['object_type']: filename,
                'path': collection,
                'location': self.b2safe_location(collection),
                'link': self.httpapi_location(
                    icom.get_absolute_path(filename, root=collection),
                    api_path=api_path,
                    remove_suffix=location)
            }

            response.append({filename: content})

        return response

    def get_batch_status(self, imain, irods_path, local_path):

        files = {}
        if not imain.is_collection(irods_path):
            return MISSING_BATCH, files

        if not local_path.exists():
            return MISSING_BATCH, files

        files = imain.list(irods_path, detailed=True)

        # Too many files on irods
        fnum = len(files)
        if fnum > 1:
            return BATCH_MISCONFIGURATION, files

        # 1 file on irods -> everything is ok
        if fnum == 1:
            return ENABLED_BATCH, files

        # No files on irods, let's check on filesystem
        files = []
        for x in local_path.glob("*"):
            if x.is_file():
                files.append(os.path.basename(str(x)))
        fnum = len(files)
        if fnum <= 0:
            return NOT_FILLED_BATCH, files

        return PARTIALLY_ENABLED_BATCH, files
