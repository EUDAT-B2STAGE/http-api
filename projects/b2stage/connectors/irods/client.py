import os
from functools import lru_cache

from flask import Response, request, stream_with_context
from irods import exception as iexceptions
from irods import models
from irods.access import iRODSAccess
from irods.manager.data_object_manager import DataObjectManager
from irods.rule import Rule
from irods.ticket import Ticket
from restapi.exceptions import RestApiException
from restapi.utilities.logs import log


class IrodsException(RestApiException):
    pass


# Mostly excluded from coverage because it is only used by a very specific service
# No further tests will be included in the core
class IrodsPythonClient:  # pragma: no cover

    anonymous_user = "anonymous"

    @staticmethod
    def get_collection_from_path(absolute_path):
        return os.path.dirname(absolute_path)

    @staticmethod
    def get_absolute_path(*args, root=None):
        if len(args) < 1:
            return root
        if root is None and not args[0].startswith("/"):
            root = "/"
        return os.path.join(root, *args)

    # ##################################
    # ##################################
    # Re-implemented wrappers
    # ##################################
    # ##################################

    def exists(self, path):
        if self.is_collection(path):
            return True
        if self.is_dataobject(path):
            return True
        return False

    def is_collection(self, path):
        try:
            return self.prc.collections.exists(path)
        except iexceptions.CAT_SQL_ERR as e:
            log.error("is_collection({}) raised CAT_SQL_ERR ({})", path, str(e))
            return False

    def is_dataobject(self, path):
        try:
            self.prc.data_objects.get(path)
            return True
        except iexceptions.CollectionDoesNotExist:
            return False
        except iexceptions.DataObjectDoesNotExist:
            return False

    def get_dataobject(self, path):
        try:
            return self.prc.data_objects.get(path)
        except (iexceptions.CollectionDoesNotExist, iexceptions.DataObjectDoesNotExist):
            raise IrodsException(f"{path} not found or no permissions")

    @staticmethod
    def getPath(path, prefix=None):
        if prefix is not None and prefix != "":
            path = path[len(prefix) :]
            if path[0] == "/":
                path = path[1:]

        return os.path.dirname(path)

    def list(
        self,
        path=None,
        recursive=False,
        detailed=False,
        acl=False,
        removePrefix=None,
        get_pid=False,
        get_checksum=False,
    ):
        """ List the files inside an iRODS path/collection """

        if path is None:
            path = self.get_user_home()

        if self.is_dataobject(path):
            raise IrodsException("Cannot list a Data Object; you may get it instead.")

        try:
            data = {}
            root = self.prc.collections.get(path)

            for coll in root.subcollections:

                row = {}
                key = coll.name
                if get_pid:
                    row["PID"] = None
                row["name"] = coll.name
                row["objects"] = {}
                if recursive:
                    row["objects"] = self.list(
                        path=coll.path,
                        recursive=recursive,
                        detailed=detailed,
                        acl=acl,
                        removePrefix=removePrefix,
                    )
                row["path"] = self.getPath(coll.path, removePrefix)
                row["object_type"] = "collection"
                if detailed:
                    row["owner"] = "-"
                if acl:
                    acl = self.get_permissions(coll)
                    row["acl"] = acl["ACL"]
                    row["acl_inheritance"] = acl["inheritance"]

                data[key] = row

            for obj in root.data_objects:

                row = {}
                key = obj.name
                row["name"] = obj.name
                row["path"] = self.getPath(obj.path, removePrefix)
                row["object_type"] = "dataobject"

                if get_pid:
                    row["PID"] = None

                if get_checksum:
                    row["checksum"] = None

                if detailed:
                    row["owner"] = obj.owner_name
                    row["content_length"] = obj.size
                    row["created"] = obj.create_time
                    row["last_modified"] = obj.modify_time
                if acl:
                    acl = self.get_permissions(obj)
                    row["acl"] = acl["ACL"]
                    row["acl_inheritance"] = acl["inheritance"]

                data[key] = row

            return data
        except iexceptions.CollectionDoesNotExist:
            raise IrodsException(f"Not found (or no permission): {path}")

        # replicas = []
        # for line in lines:
        #     replicas.append(re.split("\s+", line.strip()))
        # return replicas

    def create_empty(self, path, directory=False, ignore_existing=False):

        if directory:
            return self.create_directory(path, ignore_existing)
        else:
            return self.create_file(path, ignore_existing)

    def create_directory(self, path, ignore_existing=False):

        # print("TEST", path, ignore_existing)
        try:

            ret = self.prc.collections.create(path, recurse=ignore_existing)
            log.debug("Created irods collection: {}", path)
            return ret

        except iexceptions.CAT_UNKNOWN_COLLECTION:
            raise IrodsException("Unable to create collection, invalid path")

        except iexceptions.CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
            if not ignore_existing:
                raise IrodsException(
                    "Irods collection already exists", status_code=409,
                )
            else:
                log.debug("Irods collection already exists: {}", path)

        except (iexceptions.CAT_NO_ACCESS_PERMISSION, iexceptions.SYS_NO_API_PRIV):
            raise IrodsException(f"You have no permissions on path {path}")

        return None

    def create_file(self, path, ignore_existing=False):

        try:

            ret = self.prc.data_objects.create(path)
            log.debug("Create irods object: {}", path)
            return ret

        except iexceptions.CAT_NO_ACCESS_PERMISSION:
            raise IrodsException("CAT_NO_ACCESS_PERMISSION")

        except iexceptions.SYS_INTERNAL_NULL_INPUT_ERR:
            raise IrodsException(f"Unable to create object, invalid path: {path}")

        except iexceptions.OVERWRITE_WITHOUT_FORCE_FLAG:
            if not ignore_existing:
                raise IrodsException("Irods object already exists", status_code=400)
            log.debug("Irods object already exists: {}", path)

        return False

    def icopy(
        self,
        sourcepath,
        destpath,
        ignore_existing=False,
        warning="Irods object already exists",
    ):

        # Replace 'copy'

        dm = DataObjectManager(self.prc)

        try:
            dm.copy(sourcepath, destpath)
        except iexceptions.OVERWRITE_WITHOUT_FORCE_FLAG:
            if not ignore_existing:
                raise IrodsException("Irods object already exists", status_code=400)
            log.warning("{}: {}", warning, destpath)
        else:
            log.debug("Copied: {} -> {}", sourcepath, destpath)

    def put(self, local_path, irods_path):
        # NOTE: this action always overwrite
        return self.prc.data_objects.put(local_path, irods_path)

    def copy(
        self,
        sourcepath,
        destpath,
        recursive=False,
        force=False,
        compute_checksum=False,
        compute_and_verify_checksum=False,
    ):

        if recursive:
            log.error("Recursive flag not implemented for copy")

        if self.is_collection(sourcepath):
            raise IrodsException("Copy directory not supported")

        if compute_checksum:
            raise IrodsException("Compute_checksum not supported in copy")

        if compute_and_verify_checksum:
            raise IrodsException("Compute_and_verify_checksum not supported in copy")

        if sourcepath == destpath:
            raise IrodsException("Source and destination path are the same")
        try:
            log.verbose("Copy {} into {}", sourcepath, destpath)
            source = self.prc.data_objects.get(sourcepath)
            self.create_empty(destpath, directory=False, ignore_existing=force)
            target = self.prc.data_objects.get(destpath)
            with source.open("r+") as f:
                with target.open("w") as t:
                    for line in f:
                        # if t.writable():
                        t.write(line)
        except iexceptions.DataObjectDoesNotExist:
            raise IrodsException(
                f"DataObject not found (or no permission): {sourcepath}"
            )
        except iexceptions.CollectionDoesNotExist:
            raise IrodsException(
                f"Collection not found (or no permission): {sourcepath}"
            )

    def move(self, src_path, dest_path):

        try:
            if self.is_collection(src_path):
                self.prc.collections.move(src_path, dest_path)
                log.debug("Renamed collection: {}->{}", src_path, dest_path)
            else:
                self.prc.data_objects.move(src_path, dest_path)
                log.debug("Renamed irods object: {}->{}", src_path, dest_path)
        except iexceptions.CAT_RECURSIVE_MOVE:
            raise IrodsException("Source and destination path are the same")
        except iexceptions.SAME_SRC_DEST_PATHS_ERR:
            raise IrodsException("Source and destination path are the same")
        except iexceptions.CAT_NO_ROWS_FOUND:
            raise IrodsException("Invalid source or destination")
        except iexceptions.CAT_NAME_EXISTS_AS_DATAOBJ:
            # raised from both collection and data objects?
            raise IrodsException("Destination path already exists")
        except BaseException as e:
            log.error("{}({})", e.__class__.__name__, e)
            raise IrodsException("System error; failed to move.")

    def remove(self, path, recursive=False, force=False, resource=None):
        try:
            if self.is_collection(path):
                self.prc.collections.remove(path, recurse=recursive, force=force)
                log.debug("Removed irods collection: {}", path)
            else:
                self.prc.data_objects.unlink(path, force=force)
                log.debug("Removed irods object: {}", path)
        except iexceptions.CAT_COLLECTION_NOT_EMPTY:

            if recursive:
                raise IrodsException("Error deleting non empty directory")
            else:
                raise IrodsException(
                    "Cannot delete non empty directory without recursive flag"
                )
        except iexceptions.CAT_NO_ROWS_FOUND:
            raise IrodsException("Irods delete error: path not found")

        # FIXME: remove resource
        # if resource is not None:
        #     com = 'itrim'
        #     args = ['-S', resource]

        # Try with:
        # self.prc.resources.remove(name, test=dryRunTrueOrFalse)

    def write_file_content(self, path, content, position=0):
        try:
            obj = self.prc.data_objects.get(path)
            with obj.open("w+") as handle:

                if position > 0 and handle.seekable():
                    handle.seek(position)

                if handle.writable():

                    # handle.write('foo\nbar\n')
                    a_buffer = bytearray()
                    a_buffer.extend(map(ord, content))
                    handle.write(a_buffer)
                handle.close()
        except iexceptions.DataObjectDoesNotExist:
            raise IrodsException("Cannot write to file: not found")

    def readable(self, path):
        try:
            obj = self.prc.data_objects.get(path)
            with obj.open("r+") as handle:
                return handle.readable()
        except iexceptions.CollectionDoesNotExist:
            return False
        except iexceptions.DataObjectDoesNotExist:
            return False

    def get_file_content(self, path):
        try:
            data = []
            obj = self.prc.data_objects.get(path)
            with obj.open("r+") as handle:

                if handle.readable():

                    for line in handle:
                        s = line.decode("utf-8")
                        data.append(s)

            return data
        except iexceptions.DataObjectDoesNotExist:
            raise IrodsException("Cannot read file: not found")

    def open(self, absolute_path, destination):

        try:
            obj = self.prc.data_objects.get(absolute_path)

            # TODO: could use io package?
            with obj.open("r") as handle:
                with open(destination, "wb") as target:
                    for line in handle:
                        target.write(line)
            return True

        except iexceptions.DataObjectDoesNotExist:
            raise IrodsException("Cannot read path: not found or permssion denied")
        except iexceptions.CollectionDoesNotExist:
            raise IrodsException("Cannot read path: not found or permssion denied")
        return False

    def read_in_chunks(self, file_object, chunk_size=None):
        """
        Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k.
        """
        if chunk_size is None:
            chunk_size = self.chunk_size

        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def write_in_chunks(self, target, chunk_size=None):

        if chunk_size is None:
            chunk_size = self.chunk_size
        while True:
            chunk = request.stream.read(chunk_size)
            # print("\n\n\nCONTENT", chunk)
            if not chunk:
                break
            target.write(chunk)

    def read_in_streaming(self, absolute_path, headers=None):
        """
        Reads obj from iRODS without saving a local copy
        """

        log.info(
            "Downloading file {} in streaming with chunk size {}",
            absolute_path,
            self.chunk_size,
        )
        try:
            obj = self.prc.data_objects.get(absolute_path)

            # NOTE: what about binary option?
            handle = obj.open("r")
            if headers is None:
                headers = {}
            return Response(
                stream_with_context(self.read_in_chunks(handle, self.chunk_size)),
                headers=headers,
            )

        except iexceptions.DataObjectDoesNotExist:
            raise IrodsException("This path does not exist or permission denied")
        except iexceptions.CollectionDoesNotExist:
            raise IrodsException("This path does not exist or permission denied")

    def write_in_streaming(self, destination, force=False, resource=None):
        """
        Writes obj to iRODS without saving a local copy
        """

        # FIXME: resource is currently not used!
        # log.warning("Resource not used in saving irods data...")

        if not force and self.is_dataobject(destination):
            log.warning("Already exists")
            raise IrodsException(
                "File '"
                + destination
                + "' already exists. "
                + "Change file name or use the force parameter"
            )

        log.info(
            "Uploading file in streaming to {} with chunk size {}",
            destination,
            self.chunk_size,
        )
        try:
            self.create_empty(destination, directory=False, ignore_existing=force)
            obj = self.prc.data_objects.get(destination)

            try:
                with obj.open("w") as target:
                    self.write_in_chunks(target, self.chunk_size)

            except BaseException as ex:
                log.critical("Failed streaming upload: {}", ex)
                # Should I remove file from iRODS if upload failed?
                log.debug("Removing object from irods")
                self.remove(destination, force=True)
                raise ex

            return True

        except iexceptions.CollectionDoesNotExist:
            log.critical("Failed streaming upload: collection not found")
            raise IrodsException("Cannot write to file: path not found")
        # except iexceptions.DataObjectDoesNotExist:
        #     raise IrodsException("Cannot write to file: not found")
        except BaseException as ex:
            log.critical("Failed streaming upload: {}", ex)
            raise ex

        return False

    def save(self, path, destination, force=False, resource=None, chunk_size=None):

        if chunk_size is None:
            chunk_size = self.chunk_size

        # FIXME: resource is not used!
        # log.warning("Resource not used in saving irods data...")

        try:
            with open(path, "rb") as handle:

                self.create_empty(destination, directory=False, ignore_existing=force)

                obj = self.prc.data_objects.get(destination)

                try:
                    with obj.open("w") as target:
                        # for line in handle:
                        #     target.write(line)
                        while True:
                            piece = handle.read(chunk_size)
                            if not piece:
                                break
                            # if len(piece) > 0:
                            target.write(piece)
                except BaseException as e:
                    self.remove(destination, force=True)
                    raise e

            return True

        except iexceptions.CollectionDoesNotExist:
            raise IrodsException("Cannot write to file: path not found")
        # except iexceptions.DataObjectDoesNotExist:
        #     raise IrodsException("Cannot write to file: not found")

        return False

    ############################################
    # ############ ACL Management ##############
    ############################################

    def get_permissions(self, coll_or_obj):

        if isinstance(coll_or_obj, str):

            if self.is_collection(coll_or_obj):
                coll_or_obj = self.prc.collections.get(coll_or_obj)
            elif self.is_dataobject(coll_or_obj):
                coll_or_obj = self.prc.data_objects.get(coll_or_obj)
            else:
                coll_or_obj = None

        if coll_or_obj is None:
            raise IrodsException(
                f"Cannot get permission: path not found: {coll_or_obj}"
            )

        data = {}
        data["path"] = coll_or_obj.path
        data["ACL"] = []
        acl_list = self.prc.permissions.get(coll_or_obj)

        for acl in acl_list:
            data["ACL"].append([acl.user_name, acl.user_zone, acl.access_name])

        # FIXME: how to retrieve inheritance?
        data["inheritance"] = "N/A"

        return data

    def enable_inheritance(self, path, zone=None):

        if zone is None:
            zone = self.get_current_zone()

        key = "inherit"
        ACL = iRODSAccess(access_name=key, path=path, user_zone=zone)
        try:
            self.prc.permissions.set(ACL)  # , recursive=False)
            log.verbose("Enabled {} to {}", key, path)
        except iexceptions.CAT_INVALID_ARGUMENT:
            if not self.is_collection(path) and not self.is_dataobject(path):
                raise IrodsException("Cannot set Inherit: path not found")
            else:
                raise IrodsException("Cannot set Inherit")
            return False
        else:
            return True

    def create_collection_inheritable(self, ipath, user, permissions="own"):

        # Create the directory
        self.create_empty(ipath, directory=True, ignore_existing=True)
        # This user will own the directory
        self.set_permissions(ipath, permission=permissions, userOrGroup=user)
        # Let the permissions scale to subelements
        self.enable_inheritance(ipath)

    def set_permissions(
        self, path, permission=None, userOrGroup=None, zone=None, recursive=False
    ):

        if zone is None:
            zone = self.get_current_zone()

        # If not specified, remove permission
        if permission is None:
            permission = "null"

        try:

            ACL = iRODSAccess(
                access_name=permission, path=path, user_name=userOrGroup, user_zone=zone
            )
            self.prc.permissions.set(ACL, recursive=recursive)

            log.debug("Grant {}={} to {}", userOrGroup, permission, path)
            return True

        except iexceptions.CAT_INVALID_USER:
            raise IrodsException("Cannot set ACL: user or group not found")
        except iexceptions.CAT_INVALID_ARGUMENT:
            if not self.is_collection(path) and not self.is_dataobject(path):
                raise IrodsException("Cannot set ACL: path not found")
            else:
                raise IrodsException("Cannot set ACL")

        return False

    def set_inheritance(self, path, inheritance=True, recursive=False):

        try:
            if inheritance:
                permission = "inherit"
            else:
                permission = "noinherit"

            ACL = iRODSAccess(
                access_name=permission, path=path, user_name="", user_zone=""
            )
            self.prc.permissions.set(ACL, recursive=recursive)
            log.debug("Set inheritance {} to {}", inheritance, path)
            return True
        except iexceptions.CAT_NO_ACCESS_PERMISSION:
            if self.is_dataobject(path):
                raise IrodsException("Cannot set inheritance to a data object")
            else:
                raise IrodsException("Cannot set inheritance: collection not found")
        return False

    def get_user_home(self, user=None, append_user=True):

        zone = self.get_current_zone(prepend_slash=True)

        home = self.variables.get("home", "home")
        if home.startswith(zone):
            home = home[len(zone) :]
        home = home.lstrip("/")

        if not append_user:
            user = ""
        elif user is None:
            user = self.get_current_user()

        return os.path.join(zone, home, user)

    def get_current_user(self):
        return self.prc.username

    def get_current_zone(self, prepend_slash=False, suffix=None):
        zone = self.prc.zone
        if prepend_slash or suffix:
            zone = f"/{zone}"
        if suffix:
            return f"{zone}/{suffix}"
        else:
            return zone

    @lru_cache(maxsize=4)
    def get_user_info(self, username=None):

        if username is None:
            return None
        try:
            user = self.prc.users.get(username)
            data = {}
            data["id"] = user.id
            data["name"] = user.name
            data["type"] = user.type
            data["zone"] = user.zone
            # data["info"] = ""
            # data["comment"] = ""
            # data["create time"] = ""
            # data["modify time"] = ""
            data["account"] = user.manager.sess.pool.account.__dict__

            results = (
                self.prc.query(models.UserGroup.name)
                .filter(models.User.name == user.name)
                .get_results()
            )
            groups = []
            for obj in results:
                for _, grp in obj.items():
                    groups.append(grp)

            data["groups"] = groups
            return data
        except iexceptions.UserDoesNotExist:
            return None

    def user_has_group(self, username, groupname):
        info = self.get_user_info(username)
        if info is None:
            return False
        if "groups" not in info:
            return False
        return groupname in info["groups"]

    # TODO: merge the two following 'user_exists'
    def check_user_exists(self, username, checkGroup=None):
        userdata = self.get_user_info(username)
        if userdata is None:
            return False, f"User {username} does not exist"
        if checkGroup is not None:
            if checkGroup not in userdata["groups"]:
                return False, f"User {username} is not in group {checkGroup}"
        return True, "OK"

    def query_user_exists(self, user):
        results = (
            self.prc.query(models.User.name).filter(models.User.name == user).first()
        )

        if results is None:
            return False
        elif results[models.User.name] == user:
            return True
        else:
            raise AttributeError("Failed to query")

    def get_metadata(self, path):

        try:
            if self.is_collection(path):
                obj = self.prc.collections.get(path)
            else:
                obj = self.prc.data_objects.get(path)

            data = {}
            units = {}
            for meta in obj.metadata.items():
                name = meta.name
                data[name] = meta.value
                units[name] = meta.units

            return data, units
        except (iexceptions.CollectionDoesNotExist, iexceptions.DataObjectDoesNotExist):
            raise IrodsException("Cannot extract metadata, object not found")

    def remove_metadata(self, path, key):
        if self.is_collection(path):
            obj = self.prc.collections.get(path)
        else:
            obj = self.prc.data_objects.get(path)
        tmp = None
        for meta in obj.metadata.items():
            if key == meta.name:
                tmp = meta
                break
        # print(tmp)
        if tmp is not None:
            obj.metadata.remove(tmp)

    def set_metadata(self, path, **meta):
        try:
            if self.is_collection(path):
                obj = self.prc.collections.get(path)
            else:
                obj = self.prc.data_objects.get(path)

            for key, value in meta.items():
                obj.metadata.add(key, value)
        except iexceptions.CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
            raise IrodsException("This metadata already exist")
        except iexceptions.DataObjectDoesNotExist:
            raise IrodsException("Cannot set metadata, object not found")

    def get_user_from_dn(self, dn):
        results = (
            self.prc.query(models.User.name, models.UserAuth.user_dn)
            .filter(models.UserAuth.user_dn == dn)
            .first()
        )
        if results is not None:
            return results.get(models.User.name)
        else:
            return None

    def create_user(self, user, admin=False):

        if user is None:
            log.error("Asking for NULL user...")
            return False

        user_type = "rodsuser"
        if admin:
            user_type = "rodsadmin"

        try:
            user_data = self.prc.users.create(user, user_type)
            log.info("Created user: {}", user_data)
        except iexceptions.CATALOG_ALREADY_HAS_ITEM_BY_THAT_NAME:
            log.warning("User {} already exists in iRODS", user)
            return False

        return True

    def modify_user_password(self, user, password):
        log.debug("Changing {} password", user)
        return self.prc.users.modify(user, "password", password)

    def remove_user(self, user_name):
        user = self.prc.users.get(user_name)
        log.warning("Removing user: {}", user_name)
        return user.remove()

    def list_user_attributes(self, user):

        try:
            data = (
                self.prc.query(
                    models.User.id, models.User.name, models.User.type, models.User.zone
                )
                .filter(models.User.name == user)
                .one()
            )
        except iexceptions.NoResultFound:
            return None

        try:
            auth_data = (
                self.prc.query(models.UserAuth.user_dn)
                .filter(models.UserAuth.user_id == data[models.User.id])
                .one()
            )
            dn = auth_data.get(models.UserAuth.user_dn)
        except iexceptions.NoResultFound:
            dn = None

        return {
            "name": data[models.User.name],
            "type": data[models.User.type],
            "zone": data[models.User.zone],
            "dn": dn,
        }

    def modify_user_dn(self, user, dn, zone):

        # addAuth / rmAuth
        self.prc.users.modify(user, "addAuth", dn)
        # self.prc.users.modify(user, 'addAuth', dn, user_zone=zone)

    def rule(self, name, body, inputs, output=False):

        import textwrap

        # A bit completed to use {}.format syntax...
        rule_body = textwrap.dedent(
            """\
            %s {{
                %s
        }}"""
            % (name, body)
        )

        outname = None
        if output:
            outname = "ruleExecOut"
        myrule = Rule(self.prc, body=rule_body, params=inputs, output=outname)
        try:
            raw_out = myrule.execute()
        except BaseException as e:
            msg = f"Irule failed: {e.__class__.__name__}"
            log.error(msg)
            log.warning(e)
            raise e
        else:
            log.debug("Rule {} executed: {}", name, raw_out)

            # retrieve out buffer
            if output and len(raw_out.MsParam_PI) > 0:
                out_array = raw_out.MsParam_PI[0].inOutStruct
                # print("out array", out_array)

                import re

                file_coding = "utf-8"

                buf = out_array.stdoutBuf.buf
                if buf is not None:
                    # it's binary data (BinBytesBuf) so must be decoded
                    buf = buf.decode(file_coding)
                    buf = re.sub(r"\s+", "", buf)
                    buf = re.sub(r"\\x00", "", buf)
                    buf = buf.rstrip("\x00")
                    log.debug("Out buff: {}", buf)

                err_buf = out_array.stderrBuf.buf
                if err_buf is not None:
                    err_buf = err_buf.decode(file_coding)
                    err_buf = re.sub(r"\s+", "", err_buf)
                    log.debug("Err buff: {}", err_buf)

                return buf

            return raw_out

        #  EXAMPLE FOR IRULE: METADATA RULE
        # object_path = "/sdcCineca/home/httpadmin/tmp.txt"
        # test_name = 'paolo2'
        # inputs = {  # extra quotes for string literals
        #     '*object': f'"{object_path}"',
        #     '*name': f'"{test_name}"',
        #     '*value': f'"{test_name}"',
        # }
        # body = \"\"\"
        #     # add metadata
        #     *attribute.*name = *value;
        #     msiAssociateKeyValuePairsToObj(*attribute, *object, "-d")
        # \"\"\"
        # output = imain.irule('test', body, inputs, 'ruleExecOut')

    def ticket(self, path):
        ticket = Ticket(self.prc)
        # print("TEST", self.prc, path)
        ticket.issue("read", path)
        return ticket

    def ticket_supply(self, code):
        # use ticket for access
        ticket = Ticket(self.prc, code)
        ticket.supply()

    def test_ticket(self, path):
        # self.ticket_supply(code)

        try:
            with self.prc.data_objects.open(path, "r") as obj:
                log.verbose(obj.__class__.__name__)
        except iexceptions.SYS_FILE_DESC_OUT_OF_RANGE:
            return False
        else:
            return True

    def stream_ticket(self, path, headers=None):
        obj = self.prc.data_objects.open(path, "r")
        return Response(
            stream_with_context(self.read_in_chunks(obj, self.chunk_size)),
            headers=headers,
        )

    def list_tickets(self, user=None):

        try:
            data = self.prc.query(
                # models.Ticket.id,
                models.Ticket.string,
                models.Ticket.type,
                models.User.name,
                models.DataObject.name,
                models.Ticket.uses_limit,
                models.Ticket.uses_count,
                models.Ticket.expiration,
            ).all()
            # ).filter(User.name == user).one()

            # for obj in data:
            #     print("TEST", obj)
            #     # for _, grp in obj.items():

        except iexceptions.NoResultFound:
            return None
        else:
            return data
