# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
"""

from __future__ import absolute_import

import json
from flask import url_for
from commons.logs import get_logger
from ...confs.config import AUTH_URL
## TO FIX: check how to use the original flask response
from ..base import ExtendedApiResource
from ..services.detect import IRODS_EXTERNAL
from ..services.oauth2clients import decorate_http_request
from .. import decorators as decorate
## TO FIX: make sure the default irods admin is requested in the config file
from ..services.irods.client import IRODS_DEFAULT_ADMIN

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
        return self.force_response(response)


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
## TO BE FIXED WITH ALL THE OTHER 'response' calls
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

## TO BE FIXED:
    # move the code handling graph inside its class for authentication
    # and create a similar one with sqllite
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

        ##################################
        # Create irods user and add CN
## // TO FIX:
# Probably this code should be moved to irods class
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

        ##################################
        # Connect the user to graph If not already
        if len(user_node.associated.search(username=irods_user)) < 1:
            user_node.associated.connect(graph_irods_user)

# // TO FIX:
        """
        The error we get using the proxy cert with iRODS

Client side: GSS-API error initializing context: GSS Major Status: Communications Error
DEBUG: Client side: GSS-API error initializing context: G
SS Minor Status Error Chain:
 globus_gsi_gssapi: Error with GSS token
globus_gsi_gssapi: Error with GSS token:
 The input token has an invalid length of: 0
ERROR: [-]  iRODS/lib/core/src/clientLogin.cpp:321:clientLogin :
 status [GSI_ERROR_INIT_SECURITY_CONTEXT]  errno [] -- message []
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
