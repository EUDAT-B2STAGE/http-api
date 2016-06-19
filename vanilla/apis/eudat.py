# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
"""

from __future__ import absolute_import

import os
import json
from flask import url_for
from commons import htmlcodes as hcodes
from commons.logs import get_logger
from ...confs.config import AUTH_URL
from ..base import ExtendedApiResource
from ..services.detect import IRODS_EXTERNAL
from ..services.irods.client import IrodsException, \
    IRODS_DEFAULT_USER, IRODS_DEFAULT_ADMIN
from ..services.uploader import Uploader
from ..services.oauth2clients import decorate_http_request
from ...auth import auth
from .. import decorators as decorate
from ..services.irods.translations import DataObjectToGraph

logger = get_logger(__name__)


###############################
# Classes

class OauthLogin(ExtendedApiResource):
    """ API online test """

    base_url = AUTH_URL

    @decorate.apimethod
    def get(self):

        auth = self.global_get('custom_auth')
        b2access = auth._oauth2.get('b2access')
        response = b2access.authorize(
            callback=url_for('authorize', _external=True))
        return self.response(response)


class Authorize(ExtendedApiResource):
    """ API online test """

    base_url = AUTH_URL

    @decorate.apimethod
    def get(self):

        ############################################
        # Create the b2access object
        auth = self.global_get('custom_auth')
        b2access = auth._oauth2.get('b2access')
        # B2ACCESS requires some fixes to make this authorization call
        decorate_http_request(b2access)

        ############################################
        # Use b2access to get authorization
        resp = None
        try:
            resp = b2access.authorized_response()
        except json.decoder.JSONDecodeError as e:
            logger.critical("Authorization empty:\n%s\nCheck app credentials"
                            % str(e))
            return self.response({'errors': [{'Server misconfiguration':
                                 'oauth2 failed'}]})
        except Exception as e:
            # raise e
            logger.critical("Failed to get authorized response:\n%s" % str(e))
            return self.response(
                {'errors': [{'Access denied': 'B2ACCESS OAUTH2: ' + str(e)}]})
        if resp is None:
            return self.response(
                {'errors': [{'Access denied': 'Uknown error'}]})

        token = resp.get('access_token')
        if token is None:
            logger.critical("No token received")
            return self.response(
                {'errors': [{'External token': 'Empty token from B2ACCESS'}]})

        ############################################
        # Use b2access with token to get user info
        logger.info("Received token: '%s'" % token)
        # ## http://j.mp/b2access_profile_attributes
        from flask import session
        session['b2access_token'] = (token, '')
        current_user = b2access.get('userinfo')

        # Store b2access information inside the graphdb
        graph = self.global_get_service('neo4j')
        obj = auth.save_oauth2_info_to_user(
            graph, current_user, token)

## // TO FIX:
# make this a 'check_if_error_obj' inside the ExtendedAPIResource
        if isinstance(obj, dict) and 'errors' in obj:
            return self.response(obj)

        user_node = obj
        logger.info("Stored access info")

        ############################################
## // TO FIX:
# Move this code inside the certificates class
# as this should be done everytime the proxy expires...!
        # Get a valid certificate to access irods

        # INSECURE SSL CONTEXT. IMPORTANT: to use if not in production
        from flask import current_app
        if current_app.config['DEBUG']:
            # See more here:
            # http://stackoverflow.com/a/28052583/2114395
            import ssl
            ssl._create_default_https_context = \
                ssl._create_unverified_context
        else:
            raise NotImplementedError(
                "Do we have certificates for production?")

        from commons.certificates import Certificates
        b2accessCA = auth._oauth2.get('b2accessCA')
        obj = Certificates().make_proxy_from_ca(b2accessCA)
        if isinstance(obj, dict) and 'errors' in obj:
            return self.response(obj)

        ############################################
        # Save the proxy filename into the graph
        proxyfile = obj
        external_account_node = user_node.externals.all().pop()
        external_account_node.proxyfile = proxyfile
        external_account_node.save()

        ############################################
        # Graph linking new accounts to an iRODS user

        # irods as admin
        icom = self.global_get_service('irods', user=IRODS_DEFAULT_ADMIN)

        # Two kind of accounts
        irods_user = icom.get_translated_user(user_node.email)

        # Create irods user and add CN
        graph_irods_user = None
        try:
            graph_irods_user = graph.IrodsUser.nodes.get(username=irods_user)
        except graph.IrodsUser.DoesNotExist:

            if not IRODS_EXTERNAL:
                # Add user inside irods
                icom.create_user(irods_user)
                # Get CN from ExternalAccounts
                user_ext = list(user_node.externals.all()).pop()
                icom.admin('aua', irods_user, user_ext.certificate_cn)

            # Save into the graph
            graph_irods_user = graph.IrodsUser(username=irods_user)
            graph_irods_user.save()

        # Connect the user to graph If not already
        if len(user_node.associated.search(username=irods_user)) < 1:
            user_node.associated.connect(graph_irods_user)

# // TO FIX:

        """
        The error we get using the proxy cert with iRODS

Client side: GSS-API error initializing context: GSS Major Status: Communications Error
DEBUG: Client side: GSS-API error initializing context: GSS Minor Status Error Chain:
globus_gsi_gssapi: Error with GSS token
globus_gsi_gssapi: Error with GSS token: The input token has an invalid length of: 0
ERROR: [-]  iRODS/lib/core/src/clientLogin.cpp:321:clientLogin :  status [GSI_ERROR_INIT_SECURITY_CONTEXT]  errno [] -- message []
        """

        # # Test GSS-API
        # icom = self.global_get_service('irods', user=irods_user)
        # icom.list()

        ###################################
        # Create a valid token for our API
        token, jti = auth.create_token(auth.fill_payload(user_node))
        auth.save_token(auth._user, token, jti)
        self.set_latest_token(token)

## // TO FIX:
# Create a 'return_credentials' method to use standard Bearer oauth response
        return self.response({'token': token})


class CollectionEndpoint(ExtendedApiResource):

    @auth.login_required
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self, uuid=None):
        """
        Return list of elements inside a collection.
        If uuid is added, get the single element.
        """

        graph = self.global_get_service('neo4j')

    ##########
## // TO FIX!!
# List collections and dataobjects only linked to current user :)

        # auth = self.global_get('custom_auth')
        # graph_user = auth.get_user_object(payload=auth._payload)
        # # get the irods_user connected to graph_user
        # icom = self.global_get_service('irods', user=FIND_THE_USER)
    ##########

        content = []

        # Get ALL elements
        if uuid is None:
            content = graph.Collection.nodes.all()
        # Get SINGLE element
        else:
            try:
                content.append(graph.Collection.nodes.get(id=uuid))
            except graph.Collection.DoesNotExist:
                return self.response(errors={uuid: 'Not found.'})

        # Build jsonapi.org compliant response
        data = self.formatJsonResponse(content)
        return self.response(data)

###############
## // TO DO:
# The one above is such a standard 'get' method that
# we could make it general for the graphdb use case
###############

    @auth.login_required
    @decorate.add_endpoint_parameter('collection', required=True)
    @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def post(self):
        """ Create one collection/directory """

        icom = self.global_get_service('irods', user=IRODS_DEFAULT_USER)
        collection_input = self._args.get('collection')
        ipath = icom.create_empty(
            collection_input,
            directory=True, ignore_existing=self._args.get('force'))
        logger.info("Created irods collection: %s", ipath)

        # Save inside the graph and give back the uuid
        translate = DataObjectToGraph(
            icom=icom, graph=self.global_get_service('neo4j'))
        _, collections, zone = translate.split_ipath(ipath, with_file=False)
        node = translate.recursive_collection2node(
            collections, current_zone=zone)

        return self.response(
            {'id': node.id, 'collection': ipath},
            code=hcodes.HTTP_OK_CREATED)

    @auth.login_required
    @decorate.add_endpoint_parameter('collection', required=False)
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def delete(self, uuid):
        """ Remove an object """

        # Get the dataobject from the graph
        graph = self.global_get_service('neo4j')
        node = None
        try:
            node = graph.Collection.nodes.get(id=uuid)
        except graph.Collection.DoesNotExist:
            return self.response(errors={uuid: 'Not found.'})

        icom = self.global_get_service('irods', user=IRODS_DEFAULT_USER)
        ipath = icom.handle_collection_path(node.path)

        # Remove from graph:
        node.delete()
        # Remove from irods
        icom.remove(ipath, recursive=True)
        logger.info("Removed collection %s", ipath)

        return self.response({'deleted': ipath})


class DataObjectEndpoint(Uploader, ExtendedApiResource):

    @auth.login_required
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self, uuid=None):
        """
        Get object from ID
        """

        graph = self.global_get_service('neo4j')

        # Getting the list
        if uuid is None:
            data = self.formatJsonResponse(graph.DataObject.nodes.all())
            return self.response(data)

        # # If trying to use a path as file
        # elif name[-1] == '/':
        #     return self.response(
        #         errors={'dataobject': 'No dataobject/file requested'})

        # Do irods things
        icom = self.global_get_service('irods', user=IRODS_DEFAULT_USER)
        user = icom.get_current_user()

        # Get filename and ipath from uuid using the graph
        try:
            dataobj_node = graph.DataObject.nodes.get(id=uuid)
        except graph.DataObject.DoesNotExist:
            return self.response(errors={uuid: 'Not found.'})
        collection_node = dataobj_node.belonging.all().pop()

        # irods paths
        ipath = icom.get_irods_path(
            collection_node.path, dataobj_node.filename)

        abs_file = self.absolute_upload_file(dataobj_node.filename, user)
        # Make sure you remove any cached version to get a fresh obj
        try:
            os.remove(abs_file)
        except:
            pass

        # Execute icommand (transfer data to cache)
        icom.open(ipath, abs_file)

        # Download the file from local fs
        filecontent = super().download(
            dataobj_node.filename, subfolder=user, get=True)

        # Remove local file
        os.remove(abs_file)

        # Stream file content
        return filecontent

    @auth.login_required
    @decorate.add_endpoint_parameter('collection')
    @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def post(self):
        """
        Handle file upload
        http --form POST localhost:8080/api/dataobjects \
            file@docker-compose.test.yml
        """

        icom = self.global_get_service('irods', user=IRODS_DEFAULT_USER)
        user = icom.get_current_user()

        # Original upload
        response = super(DataObjectEndpoint, self).upload(subfolder=user)

        # If response is success, save inside the database
        key_file = 'filename'
        filename = None

        content = self.get_content_from_response(response)
        errors = self.get_content_from_response(response, get_error=True)
        status = self.get_content_from_response(response, get_status=True)

        if isinstance(content, dict) and key_file in content:
            filename = content[key_file]
            abs_file = self.absolute_upload_file(filename, user)
            logger.info("File is '%s'" % abs_file)

            ############################
            # Move file inside irods

            # ##HANDLING PATH
            # The home dir for the current user
            # Where to put the file in irods
            ipath = icom.get_irods_path(
                self._args.get('collection'), filename)

            try:
                iout = icom.save(
                    abs_file, destination=ipath, force=self._args.get('force'))
                logger.info("irods call %s", iout)
            finally:
                # Remove local cache in any case
                os.remove(abs_file)

            ######################
            # Save into graphdb
            graph = self.global_get_service('neo4j')

            translate = DataObjectToGraph(graph=graph, icom=icom)
            uuid = translate.ifile2nodes(
                ipath, service_user=self.global_get('custom_auth')._user)

            # Create response
            content = {
                'collection': ipath,
                'id': uuid
            }

        # Reply to user
        return self.response(data=content, errors=errors, code=status)

    @auth.login_required
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def delete(self, uuid):
        """ Remove an object """

        # Get the dataobject from the graph
        graph = self.global_get_service('neo4j')
        dataobj_node = graph.DataObject.nodes.get(id=uuid)
        collection_node = dataobj_node.belonging.all().pop()

        icom = self.global_get_service('irods', user=IRODS_DEFAULT_USER)
        ipath = icom.get_irods_path(
            collection_node.path, dataobj_node.filename)

        # Remove from graph:
        # Delete with neomodel the dataobject
        try:
            dataobj_node.delete()
        except graph.DataObject.DoesNotExist:
            return self.response(errors={uuid: 'Not found.'})

        # # Delete collection if not linked to any dataobject anymore?
        # if len(collection_node.belongs.all()) < 1:
        #     collection_node.delete()

        # Remove from irods
        icom.remove(ipath)
        logger.info("Removed %s", ipath)

        return self.response({'deleted': ipath})
