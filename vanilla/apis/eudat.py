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

from restapi import get_logger
logger = get_logger(__name__)


###############################
# Irods connection check
try:
    logger.info("Irods is online: %s" % test_irods)
except perror as e:
    logger.critical("Failed to connect to irods:\n%s" % str(e))


MYDEFAULTUSER = 'guest'


###############################
# Classes
class CollectionEndpoint(ExtendedApiResource):

    @decorate.apimethod
    def get(self, path=None):
        """
        Return list of elements inside a collection.
        If path is not specified we list the home directory.
        """

        icom = ICommands()
        return self.response(icom.list(path))

    @decorate.apimethod
    def post(self):
        """ Create one collection/directory """

        # handle parameters
        return self.response("Not implemented yet")


class DataObjectEndpoint(Uploader, ExtendedApiResource):

    @decorate.apimethod
    def get(self, location=None):
        """
        Get object from ID

        Note to self:
        we need to get the username from the token
        """

        # iRODS user
# // TO FIX: this should be recovered from the token
        user = MYDEFAULTUSER

        # iRODS
        icom = ICommands(user)
        try:
            iout = icom.list()
            logger.info("irods call %s", iout)
        except perror as e:
            return self.response(
                {'iRODS error': str(e)}, fail=True)

        # # GraphDB
        # logger.info("graph call %s", migraph.other())
        # query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        # migraph.cypher(query)

        return self.response({'irods': iout})

    @decorate.add_endpoint_parameter('collection')
    @decorate.apimethod
    def post(self):
        """
        Handle file upload
        """

        user = MYDEFAULTUSER

        # Original upload
        obj, status = super(DataObjectEndpoint, self).upload(subfolder=user)

        # If response is success, save inside the database
        key_file = 'filename'
        key_data = 'data'
        filename = None
        if isinstance(obj, dict) and key_file in obj[key_data]:
            filename = obj[key_data][key_file]
            abs_file = self.absolute_upload_file(filename, user)
            logger.info("File is '%s'" % abs_file)

            ############################
            # Move file inside irods

            # iRODS istance
            icom = ICommands(user)

            # ##HANDLING PATH
            # The home dir for the current user
            home = icom.get_base_dir()
            # Where to put the file in irods
            ipath = self._args.get('collection')
            # Should add the base dir if doesn't start with /
            if ipath is None:
                ipath = home
            elif ipath[0] != '/':
                ipath = home + '/' + ipath
            else:
                # Add the zone
                ipath = '/' + icom._current_environment['IRODS_ZONE'] + ipath

            # Append / if missing in the end
            if ipath[-1] != '/':
                ipath += '/'

            try:
                iout = icom.save(abs_file, destination=ipath)
                logger.info("irods call %s", iout)
            except perror as e:
                # ##HANDLING ERROR
# // TO FIX: use a decorator
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
            obj['data']['ipath'] = ipath

        # Reply to user
        return self.response(obj, code=status)
