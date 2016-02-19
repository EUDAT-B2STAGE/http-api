# -*- coding: utf-8 -*-

"""
A EUDAT endpoint example.

To discuss:
- sqlite db for users and administration
    * pluggable authentication
- upload
    * progress
    * streaming
-
"""

from ..base import ExtendedApiResource
from flask.ext.restful import request
#from werkzeug import secure_filename
from .. import decorators as decorate

from ..services.neo4j import migraph
from ..services.irodsclient import icom

# AUTH
# from confs import config
# from flask.ext.security import roles_required, auth_token_required

from restapi import get_logger
logger = get_logger(__name__)


#####################################
class DataObjectEndpoint(ExtendedApiResource):

    @decorate.apimethod
    def get(self, id=None):
        """ Get pid """

        # GraphDB
        logger.info("graph call %s", migraph.other())
        query = "MATCH (n) OPTIONAL MATCH (n)-[r]-() DELETE n,r"
        migraph.cypher(query)

        # iRODS
        # #logger.info("irods call %s", icom.list())
        logger.info("irods call %s", icom.change_user('guest'))

        return self.response(
            'There should be one or more data object here in response')

    @decorate.apimethod
    def post(self):
        """ Upload a file """

        if 'file' not in request.files:
            return "No files specified"

        myfile = request.files['file']
        #filename = secure_filename(myfile.filename)
        #destination = MYDIR + filename
        #myfile.save(destination)

        return self.response(
            "The file to be uploaded is '%s'" % myfile)
