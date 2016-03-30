# -*- coding: utf-8 -*-

"""
Prototyping!

B2SAFE HTTP REST API endpoints.
"""

from ..base import ExtendedApiResource
from flask.ext.restful import request
from .. import decorators as decorate
# from werkzeug import secure_filename

# AUTH
# from confs import config
# from flask.ext.security import roles_required, auth_token_required

#from ..services.neo4j import migraph
from ..services.irodsclient import ICommands, test_irods
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


class DataObjectEndpoint(ExtendedApiResource):

    @decorate.apimethod
    def get(self, location=None):
        """
        Get object from ID

        Note to self:
        we need to get the username from the token
        """

        # iRODS user
# // TO FIX: this should be recovered from the token
        user = 'guest'

        # iRODS
        icom = ICommands(user)
        iout = icom.list()
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

        if 'file' not in request.files:
            return "No files specified"

        myfile = request.files['file']

        # # Save the file?
        # filename = secure_filename(myfile.filename)
        # destination = MYDIR + filename
        # myfile.save(destination)

        return self.response(
            "The file to be uploaded is '%s'" % myfile)
