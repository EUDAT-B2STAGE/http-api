# -*- coding: utf-8 -*-

"""
B2ACCESS utilities
"""

import re
import json
import gssapi
from flask import session
from datetime import datetime as dt
from restapi.rest.definition import EndpointResource
from flask_oauthlib.client import OAuthResponse
from urllib3.exceptions import HTTPError

from restapi.services.oauth2clients import decorate_http_request
from utilities.certificates import Certificates
from utilities import htmlcodes as hcodes
from eudat.apis.common import IRODS_EXTERNAL, InitObj
from utilities.logs import get_logger

log = get_logger(__name__)


class B2accessUtilities(EndpointResource):

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
            log.critical("B2ACCESS empty:\n%s\nCheck app credentials" % e)
            return (b2a_token, 'Server misconfiguration: oauth2 failed')
        except Exception as e:
            # raise e  # DEBUG
            log.critical("Failed to get authorized @B2access: %s" % str(e))
            return (b2a_token, 'B2ACCESS denied. oauth2: %s' % e)
        if resp is None:
            return (b2a_token, 'B2ACCESS denied: unknown error')

        b2a_token = resp.get('access_token')
        if b2a_token is None:
            log.critical("No token received")
            return (b2a_token, 'B2ACCESS: empty token')
        log.info("Received token: '%s'" % b2a_token)
        return (b2a_token, tuple())

    def get_b2access_user_info(self, auth, b2access, b2access_token):
        """ Get user info from current b2access token """

        # To use the b2access token with oauth2 client
        # We have to save it into session
        session['b2access_token'] = (b2access_token, '')

        # Calling with the oauth2 client
        current_user = b2access.get('userinfo')
        # log.pp(current_user)

        error = True
        if current_user is None:
            errstring = "Empty response from B2ACCESS"
        elif not isinstance(current_user, OAuthResponse):
            errstring = "Invalid response from B2ACCESS"
        elif current_user.status > hcodes.HTTP_TRESHOLD:
            log.error("Bad status: %s" % str(current_user._resp))
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

        # Attributes you find: http://j.mp/b2access_profile_attributes

        # Store b2access information inside the db
        intuser, extuser = \
            auth.store_oauth2_user(current_user, b2access_token)
        # In case of error this account already existed...
        if intuser is None:
            error = "Failed to store access info"
            if extuser is not None:
                error = extuser
            return None, None, error

        log.info("Stored access info")

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
        b2access_prod = auth._oauth2.get('prod')

        # Call the oauth2 object requesting a certificate
        if self._certs is None:
            self._certs = Certificates()
        proxy_file = self._certs.proxy_from_ca(b2accessCA, prod=b2access_prod)

        # Save the proxy filename into the database
        if proxy_file is None:
            log.pp(b2accessCA, "Failed oauth2")
        else:
            auth.store_proxy_cert(extuser, proxy_file)

        return proxy_file

    def set_irods_username(self, icom, auth, user):
        """ Find out what is the irods username and save it """

        # Does this user exist?
        irods_user = icom.get_user_from_dn(user.certificate_dn)
        user_exists = irods_user is not None

        if not user_exists:
            # Production / Real B2SAFE and irods instance
            if IRODS_EXTERNAL:
                log.error("No iRODS user related to certificate")
                return None
            # Using dockerized iRODS/B2SAFE
            else:

                # NOTE: dockerized version does not know about the user
                # because it has no sync script with B2ACCESS running

                # NOTE: mapping is for common 'eudat' user for all.
                # Of course it's only for debugging purpose.
                irods_user = 'eudat'
                # irods_user = user.unity

                iadmin = self.get_service_instance(
                    service_name='irods', be_admin=True)

                # User may exist without dn/certificate
                if not iadmin.query_user_exists(irods_user):
                    # Add (as normal) user inside irods
                    iadmin.create_user(irods_user, admin=False)

                irods_user_data = iadmin.list_user_attributes(irods_user)
                if irods_user_data.get('dn') is None:
                    # Add DN to user access possibility
                    iadmin.modify_user_dn(
                        irods_user,
                        dn=user.certificate_dn, zone=irods_user_data['zone'])

        # Update db to save the irods user related to this user account
        auth.associate_object_to_attr(user, 'irodsuser', irods_user)

        # Copy certificate in the dedicated path, and update db info
        if self._certs is None:
            self._certs = Certificates()
        crt = self._certs.save_proxy_cert(
            user.proxyfile, unityid=user.unity, user=irods_user)
        auth.associate_object_to_attr(user, 'proxyfile', crt)

        return irods_user

    def check_proxy_certificate(self, extuser, e):

        # Init the error and use it in above cases
        error = str(e)

        if isinstance(e, gssapi.raw.misc.GSSError):
            # print("ECC", e)

            # Proxy renewal operations on GSS errors
            myre = r'credential:\s+([^\s]+)\s+' \
                + r'with subject:\s+([^\n]+)\s+' \
                + r'has expired\s+([0-9]+)\s+([^\s]+)\s+ago'
            pattern = re.compile(myre)
            mall = pattern.findall(error)
            if len(mall) > 0:
                m = mall.pop()
                error = "'%s' became invalid %s %s ago. " \
                    % (m[1], m[2], m[3])
                log.info(error)

                # Automatic regeneration
                if self.refresh_proxy_certificate(extuser):
                    log.info("Proxy refreshed")
                    return None
                else:
                    error = \
                        "B2ACCESS current Token is invalid or expired; " + \
                        "please request a new one at %s" % '/auth/askauth'
            else:
                # Check other proxy problems
                myre = r':\s+(Error reading[^\:\n]+:[^\n]+\n[^\n]+)\n'
                pattern = re.compile(myre)
                mall = pattern.findall(error)
                if len(mall) > 0:
                    m = mall.pop()
                    error = 'Failed credentials: %s' % m.replace('\n', '')

        return InitObj(errors=[error])

    def refresh_proxy_certificate(self, extuser):

        auth = self.auth
        proxy_file = self.obtain_proxy_certificate(auth, extuser)
        # check for errors
        if proxy_file is None:
            return False
        else:
            log.verbose("New proxy: %s" % proxy_file)

        iadmin = self.get_service_instance('irods', be_admin=True)
        irods_user = self.set_irods_username(iadmin, auth, extuser)
        log.very_verbose("Updated %s" % irods_user)

        return True
