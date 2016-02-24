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

from ..services.neo4j import migraph
from ..services.irodsclient import icom

from restapi import get_logger
logger = get_logger(__name__)


class CollectionEndpoint(ExtendedApiResource):

    @decorate.apimethod
    def get(self, path=None):
        """
        Return list of elements inside a collection.
        If path is not specified we list the home directory.
        """

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

        # GraphDB
        logger.info("graph call %s", migraph.other())
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        migraph.cypher(query)

        # iRODS
        logger.info("irods call %s", icom.change_user('guest'))
        # #logger.info("irods call %s", icom.list())

        return self.response(
            'There should be one or more data object here in response')

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
