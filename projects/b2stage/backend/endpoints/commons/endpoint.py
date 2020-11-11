"""
Common functions for EUDAT endpoints
"""

import os

from b2stage.endpoints.commons import (
    CURRENT_B2SAFE_SERVER,
    CURRENT_HTTPAPI_SERVER,
    HTTP_PROTOCOL,
    IRODS_PROTOCOL,
    IRODS_VARS,
    PRODUCTION,
    InitObj,
)
from b2stage.endpoints.commons.b2access import B2accessUtilities
from irods import exception as iexceptions
from restapi.exceptions import RestApiException
from restapi.utilities.logs import log

MISSING_BATCH = 0
NOT_FILLED_BATCH = 1
PARTIALLY_ENABLED_BATCH = 2
ENABLED_BATCH = 3
BATCH_MISCONFIGURATION = 4


class EudatEndpoint(B2accessUtilities):
    """
        Extend normal API to init
        all necessary EUDAT B2STAGE API services
    """

    _r = None  # main resources handler
    _path_separator = "/"
    _post_delimiter = "?"

    def init_endpoint(self):

        # Get user information from db, associated to token
        # NOTE: user legenda
        # internal_user = user internal to the API
        # external_user = user from oauth (B2ACCESS)
        internal_user = self.get_user()
        log.debug(
            "Token user: {} with auth method {}",
            internal_user,
            internal_user.authmethod,
        )

        #################################
        # decide which type of auth we are dealing with
        # NOTE: icom = irods commands handler (official python driver PRC)

        refreshed = False
        external_user = None

        if internal_user is None:
            raise AttributeError("Missing user association to token")

        if internal_user.authmethod == "credentials":

            icom = self.irodsuser_from_b2stage(internal_user)

        elif internal_user.authmethod == "irods":

            icom = self.irodsuser_from_b2safe(internal_user)

        elif internal_user.authmethod == "b2access":
            icom, external_user, refreshed = self.irodsuser_from_b2access(internal_user)
            # icd and ipwd do not give error with wrong credentials...
            # so the minimum command is checking the existence of home dir

            home = icom.get_user_home()
            if icom.is_collection(home):
                log.debug("{} verified", home)
            else:
                log.warning("User home not found {}", home)

        else:
            log.error("Unknown credentials provided")

        # sql = sqlalchemy.get_instance()
        # update user variable to account email, which should be always unique
        user = internal_user.email

        return InitObj(
            username=user,
            # extuser_object=external_user,
            icommands=icom,
            # db_handler=sql,
            valid_credentials=True,
            refreshed=refreshed,
        )

    def irodsuser_from_b2access(self, internal_user, refreshed=False):
        external_user = self.oauth_from_local(internal_user)

        try:
            icom = self.get_service_instance(
                service_name="irods",
                user=external_user.irodsuser,
                password=external_user.token,
                authscheme="PAM",
            )

            log.debug("Current b2access token is valid")
        except iexceptions.PAM_AUTH_PASSWORD_FAILED:

            if external_user.refresh_token is None:
                log.warning("Missing refresh token cannot request for a new token")
                raise RestApiException("Invalid PAM credentials")
            else:

                if refreshed:
                    log.info("B2access token already refreshed, cannot request new one")
                    raise RestApiException("Invalid PAM credentials")
                log.info("B2access token is no longer valid, requesting new token")

                b2access = self.create_b2access_client(self.auth, decorate=True)
                access_token = self.refresh_b2access_token(
                    self.auth,
                    external_user.email,
                    b2access,
                    external_user.refresh_token,
                )

                if access_token is not None:
                    return self.irodsuser_from_b2access(internal_user, refreshed=True)
                raise RestApiException("Failed to refresh b2access token")

        except BaseException as e:
            raise RestApiException("Unexpected error: {} ({})".format(type(e), str(e)))

        return icom, external_user, refreshed

    def irodsuser_from_b2safe(self, user):

        if user.session is not None and len(user.session) > 0:
            log.debug("Validated B2SAFE user: {}", user.uuid)
        else:
            msg = "Current credentials not registered inside B2SAFE"
            raise RestApiException(msg, status_code=401)

        try:
            return self.get_service_instance(service_name="irods", user_session=user)
        except iexceptions.PAM_AUTH_PASSWORD_FAILED:
            msg = "PAM Authentication failed, invalid password or token"
            raise RestApiException(msg, status_code=401)

        return None

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
            service_name="irods",
            only_check_proxy=True,
            user=IRODS_VARS.get("guest_user"),
            password=None,
            gss=True,
        )

        return icom

    def httpapi_location(self, ipath, api_path=None, remove_suffix=None):
        """ URI for retrieving with GET method """

        # TODO: check and clean 'remove_suffix parameter'

        # if remove_suffix is not None and uri_path.endswith(remove_suffix):
        #     uri_path = uri_path.replace(remove_suffix, '')

        if api_path is None:
            api_path = ""
        else:
            api_path = "/{}".format(api_path.lstrip("/"))

        # print("TEST", CURRENT_HTTPAPI_SERVER)

        return "{}://{}{}/{}".format(
            HTTP_PROTOCOL,
            CURRENT_HTTPAPI_SERVER,
            api_path,
            ipath.strip(self._path_separator),
        )

    def b2safe_location(self, ipath):
        return "{}://{}/{}".format(
            IRODS_PROTOCOL, CURRENT_B2SAFE_SERVER, ipath.strip(self._path_separator),
        )

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
        path = path.rstrip("/")
        if filename is not None:
            path += "/" + filename.rstrip("/")
        return path

    def parse_path(self, path):

        # If path is empty or we have a relative path return None
        # so that we can give an error
        if path is None or not os.path.isabs(path):
            return None

        if isinstance(path, str):
            return path.rstrip(self._path_separator)

        return None

    def download_object(self, r, path, head=False):
        icom = r.icommands
        username = r.username
        path = self.parse_path(path)
        is_collection = icom.is_collection(path)
        if is_collection:
            return self.send_errors(
                "Collection: recursive download is not allowed", head_method=head
            )

        if head:
            if icom.readable(path):
                return self.response("", code=200, head_method=head)
            else:
                return self.send_errors(code=404, head_method=head)

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
        filecontent = self.download(filename, subfolder=username)
        # Remove local file
        os.remove(abs_file)
        # Stream file content
        return filecontent

    def list_objects(self, icom, path, is_collection, location, public=False):
        """ DATA LISTING """

        from b2stage.connectors.irods.client import IrodsException
        from b2stage.endpoints.commons import CURRENT_MAIN_ENDPOINT, PUBLIC_ENDPOINT

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
            current_filename = path[len(collection) + 1 :]

            from contextlib import suppress

            with suppress(IrodsException):
                filelist = icom.list(path=collection)
                data = EMPTY_RESPONSE
                for filename, metadata in filelist.items():
                    if filename == current_filename:
                        data[filename] = metadata

            # # Print file details/sys metadata if it's a specific file
            # data = icom.meta_sys_list(path)

            # if a path that does not exist
            if len(data) < 1:
                return self.send_errors(
                    f"Path does not exists or you don't have privileges: {path}",
                    code=404,
                )

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

            metadata["checksum"] = checksum
            metadata["PID"] = out.get("PID")

            # Shell we add B2SAFE metadata only if present?
            metadata["EUDAT/FIXED_CONTENT"] = out.get("EUDAT/FIXED_CONTENT")
            metadata["EUDAT/REPLICA"] = out.get("EUDAT/REPLICA")
            metadata["EUDAT/FIO"] = out.get("EUDAT/FIO")
            metadata["EUDAT/ROR"] = out.get("EUDAT/ROR")
            metadata["EUDAT/PARENT"] = out.get("EUDAT/PARENT")

            metadata.pop("path")
            if public:
                api_path = PUBLIC_ENDPOINT
            else:
                api_path = CURRENT_MAIN_ENDPOINT
            content = {
                "metadata": metadata,
                metadata["object_type"]: filename,
                "path": collection,
                "location": self.b2safe_location(collection),
                "link": self.httpapi_location(
                    icom.get_absolute_path(filename, root=collection),
                    api_path=api_path,
                    remove_suffix=location,
                ),
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
