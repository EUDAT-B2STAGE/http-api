# -*- coding: utf-8 -*-

"""
Prototyping!

B2SAFE HTTP REST API endpoints.
"""

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
        user = 'betatester'

        # iRODS
        icom = ICommands(user)
        try:
            iout = icom.list()
        except perror as e:
            return self.response(
                {'iRODS error': str(e)}, fail=True)
        logger.info("irods call %s", iout)

        # # GraphDB
        # logger.info("graph call %s", migraph.other())
        # query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        # migraph.cypher(query)

        return self.response({'irods': iout})

    @decorate.apimethod
    def post(self):
        """
        Handle file upload
        """

        user = 'guest'

        # Original upload
        obj, status = super(DataObjectEndpoint, self).post(user)

        # Put to irods

        # # If response is success, save inside the database
        # key_file = 'filename'
        # key_data = 'data'
        # if isinstance(obj, dict) and key_file in obj[key_data]:
        #     logger.info("File is '%s'" % obj[key_data][key_file])

        # Reply to user
        return self.response(obj, code=status)
