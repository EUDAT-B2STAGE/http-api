# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
"""

from __future__ import absolute_import

import json
from flask import url_for
from commons.logs import get_logger
from ...confs.config import AUTH_URL
from ..base import ExtendedApiResource
from ..services.oauth2clients import decorate_http_request
## TO FIX: make sure the default irods admin is requested in the config file
from ..services.irods.client import IRODS_DEFAULT_ADMIN
from ..services.detect import IRODS_EXTERNAL
from beeprint import pp as prettyprint

# from ...auth import authentication

logger = get_logger(__name__)


###############################
# Classes

class OauthLogin(ExtendedApiResource):
    """
    Endpoint which redirects to B2ACCESS server online,
    to ask the current user for authorization/token.
    """

    base_url = AUTH_URL

    def get(self):

        auth = self.global_get('custom_auth')
        b2access = auth._oauth2.get('b2access')
        response = b2access.authorize(
            callback=url_for('authorize', _external=True))
        return self.force_response(response)


class Authorize(ExtendedApiResource):
    """
    Previous endpoint will redirect here if authorization was granted.
    Use the B2ACCESS token to retrieve info about the user,
    and to store the proxyfile.
    """

    base_url = AUTH_URL

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
            logger.critical("B2ACCESS empty:\n%s\nCheck app credentials" % e)
            return self.send_errors('Server misconfiguration', 'oauth2 failed')
        except Exception as e:
            # raise e  # DEBUG
            logger.critical("Failed to get authorized @B2access:\n%s" % str(e))
            return self.send_errors('B2ACCESS denied', 'oauth2: %s' % e)
        if resp is None:
            return self.send_errors('B2ACCESS denied', 'Uknown error')

        token = resp.get('access_token')
        if token is None:
            logger.critical("No token received")
            return self.send_errors('B2ACCESS', 'Empty token')

        ############################################
        # Use b2access with token to get user info
        logger.info("Received token: '%s'" % token)
        # http://j.mp/b2access_profile_attributes

        # Save the b2access token into session? For the next endpoint
        from flask import session
        session['b2access_token'] = (token, '')

        # All the personal data we can see from the token on B2ACCESS
        current_user = b2access.get('userinfo')
        prettyprint(current_user)

        # # Store b2access information inside the db
        user_node, external_user = auth.store_oauth2_user(current_user, token)
        # In case of error this account already existed...
        if user_node is None:
            return self.send_errors(
                'Invalid e-mail',
                'Account locally already exists with other credentials')
        else:
            logger.info("Stored access info")

        #########################
        # Get a proxy certificate to access irods
        from commons.certificates import Certificates
        b2accessCA = auth._oauth2.get('b2accessCA')
        proxyfile = Certificates().make_proxy_from_ca(b2accessCA)

        # check for errors
        if proxyfile is None:
            return self.send_errors(
                "B2ACCESS proxy",
                "Failed to create file or empty response")
        # Save the proxy filename into the database
        auth.store_proxy_cert(external_user, proxyfile)

        return "Proxy obtained"


class TestB2access(ExtendedApiResource):
    """ development tests """

    base_url = AUTH_URL

    # @authentication.authorization_required
    def get(self):

        # use this to call again b2access?
        b2access_token = "2J87ucxv5tpcHO23vysQzqH9exTShgNumREW1iVd2nk"

        # or to recover data from sql
        auth = self.global_get('custom_auth')
        internal_user, external_user = auth.oauth_from_token(b2access_token)

        #########################
        # Find out what is the irods username

        # irods as admin
        icom = self.global_get_service('irods', user=IRODS_DEFAULT_ADMIN)
        # irods related account
        irods_user = icom.get_translated_user(external_user.email)
        print("IRODS USER", irods_user)

        # Does this user exist?
        return icom.user_exists(irods_user)

        return irods_user

        # if not IRODS_EXTERNAL:
        #     # Add user inside irods
        #     icom.create_user(irods_user, admin=False)
        #     icom.admin('aua', irods_user, external_user.certificate_cn)

# #         ##################################
# #         # Create irods user inside the database
# #         graph_irods_user = None
# #         graph = self.global_get_service('neo4j')
# #         try:
# #             graph_irods_user = graph.IrodsUser.nodes.get(username=irods_user)
# #         except graph.IrodsUser.DoesNotExist:

# #             # Save into the graph
# #             graph_irods_user = graph.IrodsUser(username=irods_user)
# #             graph_irods_user.save()

#         # # Connect the user to graph If not already
#         # user_node.associated.connect(graph_irods_user)

#         # # Test GSS-API
#         # icom = self.global_get_service('irods', user=irods_user)
#         # icom.list()

#         token = "Hello World"

#         # ###################################
#         # # Create a valid token for our API
#         # token, jti = auth.create_token(auth.fill_payload(user_node))
#         # auth.save_token(auth._user, token, jti)
#         # self.set_latest_token(token)

# ## // TO FIX:
# # Create a 'return_credentials' method to use standard Bearer oauth response
#         return self.force_response({'token': token})
