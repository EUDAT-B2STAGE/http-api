# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
"""

from __future__ import absolute_import

import json
from flask import url_for, session
from ...confs.config import AUTH_URL
from ..base import ExtendedApiResource
from ..services.oauth2clients import decorate_http_request
## TO FIX: make sure the default irods admin is requested in the config file
from ..services.irods.client import \
    IrodsException, IRODS_DEFAULT_ADMIN, IRODS_DEFAULT_USER, Certificates
from ..services.detect import IRODS_EXTERNAL
from .. import decorators as decorate
from ...auth import authentication
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

    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
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

        b2access_token = resp.get('access_token')
        if b2access_token is None:
            logger.critical("No token received")
            return self.send_errors('B2ACCESS', 'Empty token')

        ############################################
        # Save the b2access token into session for oauth2client purpose
        session['b2access_token'] = (b2access_token, '')
        logger.info("Received token: '%s'" % b2access_token)
        # http://j.mp/b2access_profile_attributes

        # All the personal data we can see from the token on B2ACCESS
        current_user = b2access.get('userinfo')
        pretty_print(current_user)

        # # Store b2access information inside the db
        intuser, extuser = \
            auth.store_oauth2_user(current_user, b2access_token)
        # In case of error this account already existed...
        if intuser is None:
            return self.send_errors(
                'Invalid e-mail',
                'Account locally already exists with other credentials')
        else:
            logger.info("Stored access info")

        #########################
        # Get a proxy certificate to access irods
        b2accessCA = auth._oauth2.get('b2accessCA')
        certs = Certificates()
        proxyfile = certs.make_proxy_from_ca(b2accessCA)

        # check for errors
        if proxyfile is None:
            return self.send_errors(
                "B2ACCESS proxy",
                "Failed to create file or empty response")
        # Save the proxy filename into the database
        auth.store_proxy_cert(extuser, proxyfile)

        #########################
        # Find out what is the irods username

        # irods related account
        icom = self.global_get_service('irods')
        # irods_user = icom.get_translated_user(external.email)  # OLD
        irods_user = icom.get_user_from_dn(extuser.certificate_dn)  # NEW

        # Does this user exist?
        if irods_user is None or not icom.user_exists(irods_user):
            if IRODS_EXTERNAL:
                return self.send_errors(
                    "No iRODS user related to your certificate")
            else:
                # irods as admin
                admin_icom = self.global_get_service(
                    'irods', user=IRODS_DEFAULT_ADMIN)
                # Add user inside irods
                admin_icom.create_user(irods_user, admin=False)
                admin_icom.admin('aua', irods_user, extuser.certificate_dn)
        else:
            if not IRODS_EXTERNAL:
## // TO FIX
                print("Should we change DN associated to the existing user?")

        # Update db to save the irods user related to this extuser account
        auth.associate_object_to_attribute(extuser, 'irodsuser', irods_user)
        # Copy certificate in the dedicated path, and update db info
        crt = certs.save_proxy_cert(extuser.proxyfile, irods_user)
        auth.associate_object_to_attribute(extuser, 'proxyfile', crt)

        ###################################
        # Create a valid token for our API
        local_token, jti = auth.create_token(auth.fill_payload(intuser))
        # save it inside the current database
        auth.save_token(auth._user, local_token, jti)

# ## // TO FIX:
# # Create a 'return_credentials' method to use standard Bearer oauth response
        return {'token': local_token}


from .commons import EudatEndpoint

class RefreshProxy(EudatEndpoint):
    """ Allow refreshing of the proxy if the b2access token is still valid """

    base_url = AUTH_URL

    def get(self):
        pass


class TestB2access(ExtendedApiResource):
    """ development tests """

    base_url = AUTH_URL

    @authentication.authorization_required
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self):
        """
        Just testing
## // TO FIX: move it into common
        """

        auth = self.global_get('custom_auth')

        iuser = IRODS_DEFAULT_USER
        use_proxy = False
        _, extuser = auth.oauth_from_local(self.get_current_user())
        if extuser is not None:
            iuser = extuser.irodsuser
            use_proxy = True
        icom = self.global_get_service('irods', user=iuser, proxy=use_proxy)

        out = None
        regexp = r'The proxy credential:\s+([^\s]+)\s+' \
            + r'with subject:\s+([^\s]+)\s+expired\s+([0-9]+)\s+([^\s]+)\s+ago'

        try:
            out = icom.list()
        except Exception as e:
            import re
            pattern = re.compile(regexp)
            mall = pattern.findall(str(e))
            if len(mall) > 0:
                m = mall.pop()
                error = "'%s' became invalid %s %s ago" % (m[1], m[2], m[3])
                return self.send_errors('Expired proxy credential', error)
            else:
                raise e

        return out
        # return [internal.email, external.proxyfile, external.irodsuser]
