# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
"""

from __future__ import absolute_import

import json
from datetime import datetime as dt
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


class B2accessUtilities(EudatEndpoint):
    """
    Utilities to use B2ACCESS
    """

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
        if current_app.config['DEBUG']:
            pretty_print(resp)  # DEBUG

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

        # Get token expiration time
        response = b2access.get('tokeninfo')
        timestamp = response.data.get('exp')

        timestamp_resolution = 1
        # timestamp_resolution = 1e3

        # Convert into datetime object and save it inside db
        token_exp = dt.fromtimestamp(int(timestamp) / timestamp_resolution)
        auth.associate_object_to_attr(extuser, 'token_expiration', token_exp)

        return intuser, extuser

    def obtain_proxy_certificate(self, auth, extuser):
        """
        Ask B2ACCESS a valid proxy certificate to access irods data.

        Note: this certificates lasts 12 hours.
        """

        # To use the b2access token with oauth2 client
        # We have to save it into session
        key = 'b2access_token'
        if key not in session or session.get(key, None) is None:
            session[key] = (extuser.token, '')

        # # invalidate token, for debug purpose
        # session[key] = ('ABC', '')

        # Create the object for accessing certificates in B2ACCESS
        b2accessCA = auth._oauth2.get('b2accessCA')

        # Call the oauth2 object requesting a certificate
        if self._certs is None:
            self._certs = Certificates()
        proxy_file = self._certs.make_proxy_from_ca(b2accessCA)

        # Save the proxy filename into the database
        if proxy_file is not None:
            auth.store_proxy_cert(extuser, proxy_file)

        return proxy_file

    def set_irods_username(self, auth, extuser):
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


class Authorize(B2accessUtilities):
    """
    Previous endpoint will redirect here if authorization was granted.
    Use the B2ACCESS token to retrieve info about the user,
    and to store the proxyfile.
    """

    base_url = AUTH_URL

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
        intuser, extuser = \
            self.get_b2access_user_info(auth, b2access, b2access_token)
        proxy_file = self.obtain_proxy_certificate(auth, extuser)
        # check for errors
        if proxy_file is None:
            return self.send_errors(
                "B2ACCESS proxy", "Cannot get file or unauthorized response")

        self.set_irods_username(auth, extuser)

        # If all is well, give our local token to this validated user
        local_token, jti = auth.create_token(auth.fill_payload(intuser))
        auth.save_token(auth._user, local_token, jti)

# ## // TO FIX:
# # Create a 'return_credentials' method to use standard Bearer oauth response
        return {'token': local_token}


class B2accesProxyEndpoint(B2accessUtilities):
    """
    Allow refreshing current proxy (if invalid)
    using the stored b2access token (if still valid)
    """

    base_url = AUTH_URL

    @authentication.authorization_required
    def post(self):

        ##########################
        # get the response
        r = self.init_endpoint(only_check_proxy=True)
        # pretty_print(r)
        if r.errors is not None:
            return self.send_errors(errors=r.errors)

        ##########################
        # verify what happened
        if r.valid_credentials:
            logger.debug("A valid proxy already exists")
            return {"Completed": "Current proxy is still valid."}

        auth = self.global_get('custom_auth')
        proxy_file = self.obtain_proxy_certificate(auth, r.extuser_object)

        # check for errors
        if proxy_file is None:
            return self.send_errors(
                "B2ACCESS proxy",
                "B2ACCESS current token is invalid or expired. " +
                "Please request a new one at /auth/askauth.")
        self.set_irods_username(auth, r.extuser_object)
        logger.info("Refreshed with a new proxy: %s" % proxy_file)

        return {"Completed": "New proxy was generated."}


# class TestB2access(B2accessUtilities):
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
        pretty_print(r)

        ##########################
        return {'list': r.icommands.list()}
