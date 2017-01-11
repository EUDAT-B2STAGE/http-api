# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
"""

from __future__ import absolute_import

import json
from datetime import datetime as dt
from flask import url_for, session, current_app, request
from flask_oauthlib.client import OAuthResponse
from urllib3.exceptions import HTTPError
from ...confs.config import API_URL, AUTH_URL, \
    PRODUCTION, DEBUG as ENVVAR_DEBUG
from ..services.oauth2clients import decorate_http_request
from ..services.irods.client import IrodsException, Certificates
from ..services.detect import IRODS_EXTERNAL
from .. import decorators as decorate
from ...auth import authentication
from .commons import EudatEndpoint
from commons import htmlcodes as hcodes
from commons.logs import get_logger, pretty_print

logger = get_logger(__name__)


###############################
# Classes

class B2accessUtilities(EudatEndpoint):
    """ All utilities to use B2ACCESS """
    _certs = None

    def create_b2access_client(self, auth, decorate=False):
        """ Create the b2access Flask oauth2 object """

        b2access = auth._oauth2.get('b2access')
        # B2ACCESS requires some fixes to make authorization work...
        if decorate:
            decorate_http_request(b2access)
        return b2access

    def request_b2access_token(self, b2access):
        """ Use b2access client to get a token for all necessary operations """
        resp = None
        b2a_token = None

        try:

            resp = b2access.authorized_response()
        except json.decoder.JSONDecodeError as e:
            logger.critical("B2ACCESS empty:\n%s\nCheck app credentials" % e)
            return (b2a_token, ('Server misconfiguration', 'oauth2 failed'))
        except Exception as e:
            # raise e  # DEBUG
            logger.critical("Failed to get authorized @B2access: %s" % str(e))
            return (b2a_token, ('B2ACCESS denied', 'oauth2: %s' % e))
        if resp is None:
            return (b2a_token, ('B2ACCESS denied', 'Uknown error'))

        DEBUG_PRINT = current_app.config['DEBUG'] or ENVVAR_DEBUG
        if DEBUG_PRINT:
            pretty_print(resp)  # DEBUG

        b2a_token = resp.get('access_token')
        if b2a_token is None:
            logger.critical("No token received")
            return (b2a_token, ('B2ACCESS', 'Empty token'))
        logger.info("Received token: '%s'" % b2a_token)
        return (b2a_token, tuple())

    def get_b2access_user_info(self, auth, b2access, b2access_token):
        """ Get user info from current b2access token """

        # To use the b2access token with oauth2 client
        # We have to save it into session
        session['b2access_token'] = (b2access_token, '')

        # Calling with the oauth2 client
        current_user = b2access.get('userinfo')

        error = True
        if current_user is None:
            errstring = "Empty response from B2ACCESS"
        elif not isinstance(current_user, OAuthResponse):
            errstring = "Invalid response from B2ACCESS"
        elif current_user.status > hcodes.HTTP_TRESHOLD:
            logger.error("Bad status: %s" % str(current_user._resp))
            if current_user.status == hcodes.HTTP_BAD_UNAUTHORIZED:
                errstring = "B2ACCESS token obtained is unauthorized..."
            else:
                errstring = "B2ACCESS token obtained failed with %s" \
                    % current_user.status
        elif isinstance(current_user._resp, HTTPError):
            errstring = "Error from B2ACCESS: %s" % current_user._resp
        else:
            error = False

        if error:
            return None, None, errstring

        DEBUG_PRINT = current_app.config['DEBUG'] or ENVVAR_DEBUG
        if DEBUG_PRINT:
            # Attributes you find: http://j.mp/b2access_profile_attributes
            pretty_print(current_user)  # DEBUG

        # Store b2access information inside the db
        intuser, extuser = \
            auth.store_oauth2_user(current_user, b2access_token)
        # In case of error this account already existed...
        if intuser is None:
            error = "Failed to store access info"
            if extuser is not None:
                error = extuser
            return None, None, error

        logger.info("Stored access info")

        # Get token expiration time
        response = b2access.get('tokeninfo')
        timestamp = response.data.get('exp')

        timestamp_resolution = 1
        # timestamp_resolution = 1e3

        # Convert into datetime object and save it inside db
        tok_exp = dt.fromtimestamp(int(timestamp) / timestamp_resolution)
        auth.associate_object_to_attr(extuser, 'token_expiration', tok_exp)

        return current_user, intuser, extuser

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
        prod = PRODUCTION and (ENVVAR_DEBUG is None or not ENVVAR_DEBUG)
        proxy_file = self._certs.make_proxy_from_ca(b2accessCA, prod=prod)

        # Save the proxy filename into the database
        if proxy_file is not None:
            auth.store_proxy_cert(extuser, proxy_file)
        else:
            pretty_print(b2accessCA, "Failed oauth2")

        return proxy_file

    def set_irods_username(self, icom, auth, extuser, unityid='eudat_guest'):
        """ Find out what is the irods username and save it """

        # irods_user = icom.get_translated_user(external.email)  # OLD
        irods_user = icom.get_user_from_dn(extuser.certificate_dn)  # NEW

        # Does this user exist?
        user_exists = irods_user is not None and icom.user_exists(irods_user)

        # Production / Real B2SAFE and irods instance
        if IRODS_EXTERNAL:
            #logger.error("No iRODS user related to your certificate")
            if not user_exists:
                return None
        # IN CASE WE ARE USING DOCKERIZED iRODS/B2SAFE
        else:
            # irods admin user handler
            admin_icom = self.global_get_service('irods', become_admin=True)

            if user_exists:
                # recover the old/current one
                tmp = admin_icom.admin('lua', irods_user)
                current_dn = tmp.splitlines()[0].strip().split(" ", 1)[1]
                # remove the old one
                admin_icom.admin('rua', irods_user, current_dn)
            else:
                irods_user = unityid

                # Add (as normal) user inside irods
                admin_icom.create_user(irods_user, admin=False)

            # Add DN to user access possibility
            admin_icom.admin('aua', irods_user, extuser.certificate_dn)

        # Update db to save the irods user related to this extuser account
        auth.associate_object_to_attr(extuser, 'irodsuser', irods_user)

        # Copy certificate in the dedicated path, and update db info
        if self._certs is None:
            self._certs = Certificates()
        crt = self._certs.save_proxy_cert(extuser.proxyfile, irods_user)
        auth.associate_object_to_attr(extuser, 'proxyfile', crt)

        return irods_user


#######################################
#######################################
class OauthLogin(B2accessUtilities):
    """
    Endpoint which redirects to B2ACCESS server online,
    to ask the current user for authorization/token.
    """

    base_url = AUTH_URL

    def get(self):

        auth = self.global_get('custom_auth')
        b2access = self.create_b2access_client(auth)

        authorized_uri = url_for('authorize', _external=True)
        if PRODUCTION:
            # What needs a fix:
            # http://awesome.docker:443/auth/authorize
            # curl -i -k https://awesome.docker/auth/askauth
            authorized_uri = authorized_uri \
                .replace('http:', 'https:') \
                .replace(':443', '')

        logger.info("Ask redirection to: %s" % authorized_uri)

        response = b2access.authorize(callback=authorized_uri)
        return self.force_response(response)


#######################################
#######################################
class Authorize(B2accessUtilities):
    """
    Previous endpoint will redirect here if authorization was granted.
    Use the B2ACCESS token to retrieve info about the user,
    and to store the proxyfile.
    """

    base_url = AUTH_URL

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self):
        """
        Get the data for upcoming operations.

        Note: all of this actions are based on our user to have granted
        permissions to access his profile data.
        """

        # Get b2access token
        auth = self.global_get('custom_auth')
        b2access = self.create_b2access_client(auth, decorate=True)
        b2access_token, b2access_errors = self.request_b2access_token(b2access)
        if b2access_token is None:
            return self.send_errors(*b2access_errors)

        # B2access user info
        curuser, intuser, extuser = \
            self.get_b2access_user_info(auth, b2access, b2access_token)
        if curuser is None and intuser is None:
            return self.send_errors('oauth2', extuser)

        # B2access user proxy
        proxy_file = self.obtain_proxy_certificate(auth, extuser)
        if proxy_file is None:
            return self.send_errors(
                "B2ACCESS CA is down", "Could not get certificate files")

        # iRODS related
        # NOTE: this irods client uses default admin to find the related user
        icom = self.global_get_service('irods')
        uid = self.username_from_unity(curuser.data.get('unity:persistent'))
        irods_user = self.set_irods_username(icom, auth, extuser, uid)
        if irods_user is None:
            return self.send_errors(
                "Failed to set irods user from: %s/%s" % (uid, extuser))
        user_home = icom.get_user_home(irods_user)

        # If all is well, give our local token to this validated user
        local_token, jti = auth.create_token(auth.fill_payload(intuser))
        auth.save_token(auth._user, local_token, jti)

        uri = self.httpapi_location(
            request.url.replace("/auth/authorize", ''),
            API_URL + "/namespace" + user_home
        )

        get_example = "curl -H 'Authorization: %s %s' %s" \
            % ('Bearer', local_token, uri)

        # TO FIX: Create a method to reply with standard Bearer oauth response
        # return self.send_credentials(local_token, extra, metas)

        return self.force_response(
            defined_content={
                'token': local_token,
                'b2safe_user': irods_user,
                'b2safe_home': user_home
            },
            meta={
                'examples': {
                    'get': get_example
                }
            }
        )


#######################################
#######################################
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
            if r.is_proxy:
                logger.debug("A valid proxy already exists")
                return {"Completed": "Current proxy is still valid."}
            else:
                logger.debug("Current user does not use a proxy")
                return {"Skipped": "Not using a certificate proxy."}

        auth = self.global_get('custom_auth')
        proxy_file = self.obtain_proxy_certificate(auth, r.extuser_object)

        # check for errors
        if proxy_file is None:
            return self.send_errors(
                "B2ACCESS proxy",
                "B2ACCESS current Token is invalid or expired. " +
                "Please request a new one at /auth/askauth.",
                code=hcodes.HTTP_BAD_UNAUTHORIZED)

        irods_user = self.set_irods_username(
            r.icommands, auth, r.extuser_object, r.extuser_object.unity)
        if irods_user is None:
            return self.send_errors(
                "Failed to set irods user from: %s" % r.extuser_object)
        logger.info("Refreshed with a new proxy: %s" % proxy_file)

        return {"Completed": "New proxy was generated."}


#######################################
# JUST TO TEST
#######################################

# # class TestB2access(B2accessUtilities):
# class TestB2access(EudatEndpoint):
#     """ development tests """

#     base_url = AUTH_URL

#     @authentication.authorization_required
#     @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
#     def get(self):

#         ##########################
#         # get the response
#         r = self.init_endpoint()
#         # pretty_print(r)
#         if r.errors is not None:
#             return self.send_errors(errors=r.errors)
#         pretty_print(r)

#         ##########################
#         return {'list': r.icommands.list()}
