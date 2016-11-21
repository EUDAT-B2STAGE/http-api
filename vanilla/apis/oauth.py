# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
"""

from __future__ import absolute_import

import json
from flask import url_for, session, current_app
from ...confs.config import AUTH_URL
from ..base import ExtendedApiResource
from ..services.oauth2clients import decorate_http_request
from ..services.irods.client import \
    IrodsException, IRODS_DEFAULT_ADMIN, Certificates
from ..services.detect import IRODS_EXTERNAL
from .. import decorators as decorate
from ...auth import authentication
from .commons import EudatEndpoint
from commons.logs import get_logger, pretty_print

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
    _certs = None

    def create_b2access_client(self, auth):
        """ Create the b2access Flask oauth2 object """

        b2access = auth._oauth2.get('b2access')
        # B2ACCESS requires some fixes to make authorization work...
        decorate_http_request(b2access)
        return b2access

    def request_b2access_token(self, b2access):
        """ Use b2access client to get a token for all necessary operations """
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

        b2access_token = resp.get('access_token')
        if b2access_token is None:
            logger.critical("No token received")
            return self.send_errors('B2ACCESS', 'Empty token')
        logger.info("Received token: '%s'" % b2access_token)
        return b2access_token

    def get_b2access_user_info(self, auth, b2access, b2access_token):
        """ Get user info from current b2access token """

        # To use the b2access token with oauth2 client
        # We have to save it into session
        session['b2access_token'] = (b2access_token, '')

        # Calling with the oauth2 client
        current_user = b2access.get('userinfo')
        if current_app.config['DEBUG']:
            # Attributes you find: http://j.mp/b2access_profile_attributes
            pretty_print(current_user)  # DEBUG

        # Store b2access information inside the db
        intuser, extuser = \
            auth.store_oauth2_user(current_user, b2access_token)
        # In case of error this account already existed...
        if intuser is None:
            return self.send_errors(
                'Invalid e-mail',
                'Account locally already exists with other credentials')
        else:
            logger.info("Stored access info")

        return current_user, intuser, extuser

    def obtain_proxy_certificate(self, auth, extuser):
        """
        Ask B2ACCESS a valid proxy certificate to access irods data.

        Note: this certificates lasts 12 hours.
        """

        # To use the b2access token with oauth2 client
        # We have to save it into session
        session['b2access_token'] = (extuser.token, '')

        # Create the object for accessing certificates in B2ACCESS
        b2accessCA = auth._oauth2.get('b2accessCA')

        # Call the oauth2 object requesting a certificate
        if self._certs is None:
            self._certs = Certificates()
        proxy_file = self._certs.make_proxy_from_ca(b2accessCA)

        # check for errors
        if proxy_file is None:
            return self.send_errors(
                "B2ACCESS proxy",
                "Failed to create file or empty response")

        # Save the proxy filename into the database
        auth.store_proxy_cert(extuser, proxy_file)

        return proxy_file

    def set_irods_username(self, auth, curuser, extuser):
        """ Find out what is the irods username and save it """

        icom = self.global_get_service('irods')
        if not IRODS_EXTERNAL:
            # irods as admin
            admin_icom = self.global_get_service(
                'irods', user=IRODS_DEFAULT_ADMIN)

        # irods_user = icom.get_translated_user(external.email)  # OLD
        irods_user = icom.get_user_from_dn(extuser.certificate_dn)  # NEW

        # Does this user exist?
        if irods_user is None or not icom.user_exists(irods_user):
            if IRODS_EXTERNAL:
                return self.send_errors(
                    "No iRODS user related to your certificate")
            else:
                # Add user inside irods (if using local irods with docker)
                admin_icom.create_user(irods_user, admin=False)
                admin_icom.admin('aua', irods_user, extuser.certificate_dn)
        else:
            # Update DN for current irods user
            if not IRODS_EXTERNAL:
                # recover the old/current one
                tmp = admin_icom.admin('lua', irods_user)
                current_dn = tmp.strip().split()[1]
                # remove the old one
                admin_icom.admin('rua', irods_user, current_dn)
                # add the new one
                admin_icom.admin('aua', irods_user, extuser.certificate_dn)

        # Update db to save the irods user related to this extuser account
        auth.associate_object_to_attr(extuser, 'irodsuser', irods_user)
        # Copy certificate in the dedicated path, and update db info
        if self._certs is None:
            self._certs = Certificates()
        crt = self._certs.save_proxy_cert(extuser.proxyfile, irods_user)
        auth.associate_object_to_attr(extuser, 'proxyfile', crt)

        return irods_user

    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self):
        """
        Get the data for upcoming operations.

        Note: all of this actions are based on our user to have granted
        permissions to access his profile data.
        """

        # Get b2access token
        auth = self.global_get('custom_auth')
        b2access = self.create_b2access_client(auth)
        b2access_token = self.request_b2access_token(b2access)

        # Get user info and certificate
        curuser, intuser, extuser = \
            self.get_b2access_user_info(auth, b2access, b2access_token)
        self.obtain_proxy_certificate(auth, extuser)
        self.set_irods_username(auth, curuser, extuser)

        # If all is well, give our local token to this validated user
        local_token, jti = auth.create_token(auth.fill_payload(intuser))
        auth.save_token(auth._user, local_token, jti)

# ## // TO FIX:
# # Create a 'return_credentials' method to use standard Bearer oauth response
        return {'token': local_token}


# class Proxy(EudatEndpoint):
#     """
#     Endpoint to let the user manage their b2access proxy?
#     """

#     base_url = AUTH_URL

#     @authentication.authorization_required
#     def get(self):

#         pass

#         # _, extuser = self.init_endpoint(only_check_proxy=True)
#         # return {'proxy_file': extuser.proxyfile}


class RefreshProxy(EudatEndpoint):
    """
    Allow refreshing current proxy (if invalid)
    using the stored b2access token (if still valid)
    """

    base_url = AUTH_URL

    @authentication.authorization_required
    def get(self):

        ##########################
        # get the response
        r = self.init_endpoint(only_check_proxy=True)
        # pretty_print(r)
        if r.errors is not None:
            return self.send_errors(errors=r.errors)

        ##########################
        # verify what happened
        if not r.valid_credentials:
            auth = self.global_get('custom_auth')
            proxy_file = self.obtain_proxy_certificate(auth, r.extuser_object)
            logger.info("Refreshed with a new proxy: %s" % proxy_file)
        else:
            logger.debug("A valid proxy already exists")

        return {"message": "Operation completed"}


class TestB2access(EudatEndpoint):
    """ development tests """

    base_url = AUTH_URL

    @authentication.authorization_required
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self):

        ##########################
        # get the response
        r = self.init_endpoint()
        # pretty_print(r)
        if r.errors is not None:
            return self.send_errors(errors=r.errors)

        ##########################
        return {'list': r.icommands.list()}
