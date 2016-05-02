# -*- coding: utf-8 -*-

"""
Prototyping!

B2SAFE HTTP REST API endpoints.
"""

import os
from ..base import ExtendedApiResource
# from flask.ext.restful import request
from .. import decorators as decorate
# from werkzeug import secure_filename

# AUTH
# from confs import config
# from flask.ext.security import roles_required, auth_token_required

# from ..services.neo4j import migraph
from ..services.irodsclient import ICommands, test_irods
from ..services.uploader import Uploader
from plumbum.commands.processes import ProcessExecutionError as perror
from ... import htmlcodes as hcodes

from restapi import get_logger
logger = get_logger(__name__)


###############################
# Irods connection check
try:
    logger.info("Irods is online: %s" % test_irods)
except perror as e:
    logger.critical("Failed to connect to irods:\n%s" % str(e))


###############################
# Classes
class IrodsEndpoints(ExtendedApiResource):

    def get_token_user(self):
        """
        WARNING: NOT IMPLEMENTED YET!

        This will depend on B2ACCESS authentication
        """
# // TO FIX: this should be recovered from the token
        return 'guest'

    def get_instance(self):
        user = self.get_token_user()
        # iRODS object
        return ICommands(user)

    def handle_collection_path(self, icom, ipath):

        home = icom.get_base_dir()

        # Should add the base dir if doesn't start with /
        if ipath is None or ipath == '':
            ipath = home
        elif ipath[0] != '/':
            ipath = home + '/' + ipath
        else:
            # Add the zone
            ipath = '/' + icom._current_environment['IRODS_ZONE'] + ipath
        # Append / if missing in the end
        if ipath[-1] != '/':
            ipath += '/'

        return ipath


class GraphEndpoints(ExtendedApiResource):

    def get_instance(self):

        # # GraphDB connection ?
        # logger.info("graph call %s", migraph.other())
        # query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        # migraph.cypher(query)
        return False


class CollectionEndpoint(IrodsEndpoints):

    @decorate.apimethod
    def get(self, path=None):
        """
        Return list of elements inside a collection.
        If path is not specified we list the home directory.
        """

        icom = self.get_instance()
        return self.response(icom.list(path))

    @decorate.add_endpoint_parameter('collection', required=True)
    @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.apimethod
    def post(self):
        """ Create one collection/directory """

        icom = self.get_instance()
        ipath = self._args.get('collection')

        try:
            icom.create_empty(
                ipath, directory=True, ignore_existing=self._args.get('force'))
            logger.info("irods made collection: %s", ipath)
        except perror as e:
            # ##HANDLING ERROR
# // TO FIX: use a decorator
            error = str(e)
            if 'ERROR:' in error:
                error = error[error.index('ERROR:')+7:]
            return self.response({'iRODS error': error}, fail=True)

        return self.response(ipath, code=hcodes.HTTP_OK_CREATED)


class DataObjectEndpoint(Uploader, IrodsEndpoints):

    @decorate.add_endpoint_parameter('collection')
    @decorate.apimethod
    def get(self, name=None):
        """
        Get object from ID

        Note to self:
        we need to get the username from the token
        """

        if name is None or name[-1] == '/':
            return self.response(
                {'dataobject': 'No dataobject/file requested'}, fail=True)

        # obj init
        user = self.get_token_user()
        icom = self.get_instance()

        # paths
        collection = self.handle_collection_path(
            icom, self._args.get('collection'))
        ipath = collection + name
        abs_file = self.absolute_upload_file(name, user)

# // TO FIX: use cache?
        # Remove files in cache for now
        try:
            os.remove(abs_file)
        except:
            pass
        # print("Requested name", name, collection, name)

        # Move the irods file into local fs
        try:
            icom.open(ipath, abs_file)
        except perror as e:
            error = str(e)
            if 'ERROR:' in error:
                    error = error[error.index('ERROR:')+7:]
            return self.response(
                {'iRODS error': error}, fail=True)

        # Download the file from local fs
        filecontent = super().download(
            name, subfolder=user, get=True)

        # Remove local file
        os.remove(abs_file)

        # Stream file content
        return filecontent

    @decorate.add_endpoint_parameter('collection')
    @decorate.apimethod
    def post(self):
        """
        Handle file upload
        """

        user = self.get_token_user()

        # Original upload
        obj, status = super(DataObjectEndpoint, self).upload(subfolder=user)

        # If response is success, save inside the database
        key_file = 'filename'
        key_data = 'data'
        key_response = 'Response'
        filename = None
        if isinstance(obj, dict) and key_file in obj[key_response][key_data]:
            filename = obj[key_response][key_data][key_file]
            abs_file = self.absolute_upload_file(filename, user)
            logger.info("File is '%s'" % abs_file)

            ############################
            # Move file inside irods
            icom = self.get_instance()

            # ##HANDLING PATH
            # The home dir for the current user
            # Where to put the file in irods
            collection = self.handle_collection_path(
                icom, self._args.get('collection'))
            ipath = collection + filename

            try:
                iout = icom.save(abs_file, destination=ipath)
                logger.info("irods call %s", iout)
            except perror as e:
                # ##HANDLING ERROR
                # Remove local
                os.remove(abs_file)
                error = str(e)
                if 'Stdout:' in error:
                    error = error[error.index('Stdout:')+9:]
                elif 'ERROR:' in error:
                    error = error[error.index('ERROR:')+7:]
                return self.response({'iRODS error': error}, fail=True)

            # Remove actual file (if we do not want to cache)
            os.remove(abs_file)
            obj['Response']['data']['collection'] = ipath

        # Reply to user
        return self.response(obj, code=status)

    @decorate.add_endpoint_parameter('collection')
    @decorate.apimethod
    def delete(self, name):
        """ Remove an object """

        icom = self.get_instance()
        # paths
        collection = self.handle_collection_path(
            icom, self._args.get('collection'))
        ipath = collection + name
        try:
            iout = icom.remove(ipath)
            logger.info("irods call %s", iout)
        except perror as e:
            error = str(e)
            if 'ERROR:' in error:
                error = error[error.index('ERROR:')+7:]
            return self.response({'iRODS error': error}, fail=True)

        return self.response({'deleted': ipath})
