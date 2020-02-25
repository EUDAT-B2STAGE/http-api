# -*- coding: utf-8 -*-

"""
OAUTH2 authentication with EUDAT services
"""

from flask import url_for

from b2stage.apis.commons import PRODUCTION
from b2stage.apis.commons.endpoint import EudatEndpoint

from restapi.flask_ext.flask_irods.client import IrodsException
from restapi import decorators as decorate
from restapi.protocols.bearer import authentication

from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class OauthLogin(EudatEndpoint):
    """
    Endpoint which redirects to B2ACCESS server online,
    to ask the current user for authorization/token.
    """

    baseuri = '/auth'
    labels = ['eudat', 'b2access', 'authentication']
    depends_on = ['B2ACCESS_APPKEY']
    GET = {
        '/askauth': {
            'custom': {},
            'summary': 'Redirection to B2ACCESS oauth2 login',
            'responses': {'200': {'description': 'redirected'}},
        }
    }

    @decorate.catch_error(
        exception=RuntimeError, exception_label='Server side B2ACCESS misconfiguration'
    )
    def get(self):

        from restapi.rest.response import request_from_browser

        if not request_from_browser():
            return self.send_errors(
                "B2ACCESS authorization must be requested from a browser",
                code=hcodes.HTTP_BAD_METHOD_NOT_ALLOWED,
            )

        auth = self.auth
        b2access = self.create_b2access_client(auth)

        authorized_uri = url_for('authorize', _external=True)
        if PRODUCTION:
            # What needs a fix:
            # http://awesome.docker:443/auth/authorize
            # curl -i -k https://awesome.docker/auth/askauth
            authorized_uri = authorized_uri.replace('http:', 'https:').replace(
                ':443', ''
            )

        log.info("Ask redirection to: {}", authorized_uri)

        response = b2access.authorize(callback=authorized_uri)
        return self.force_response(response)


class Authorize(EudatEndpoint):
    """
    Previous endpoint will redirect here if authorization was granted.
    Use the B2ACCESS token to retrieve info about the user
    """

    baseuri = '/auth'
    labels = ['eudat', 'b2access', 'authentication']
    depends_on = ['B2ACCESS_APPKEY']
    GET = {
        '/authorize': {
            'custom': {},
            'summary': 'Produce internal token if B2ACCESS authorization is granted',
            'responses': {
                '200': {'description': 'REST API token from B2ACCESS authentication'}
            },
        }
    }

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self):
        """
        Get the data for upcoming operations.

        Note: all of this actions are based on our user to have granted
        permissions to access his profile data.
        """

        # Get b2access token
        auth = self.auth
        b2access = self.create_b2access_client(auth, decorate=True)
        b2access_token, b2access_refresh_token, b2access_error = self.request_b2access_token(
            b2access
        )
        if b2access_token is None:
            return self.send_errors(message=b2access_error)

        # B2access user info
        b2access_user, intuser, extuser = self.get_b2access_user_info(
            auth, b2access, b2access_token, b2access_refresh_token
        )
        if b2access_user is None and intuser is None:
            return self.send_errors(
                message='Unable to retrieve user info from b2access', errors=extuser
            )

        b2access_email = b2access_user.data.get('email')
        log.info("B2ACCESS email = {}", b2access_email)

        imain = self.get_main_irods_connection()

        irods_user = self.get_irods_user_from_b2access(imain, b2access_email)

        if irods_user is None:
            err = "B2ACCESS credentials ({}) do not match any user in B2SAFE".format(
                b2access_email)
            log.error(err)
            return self.send_errors(err)

        # Update db to save the irods user related to this user account
        self.associate_object_to_attr(extuser, 'irodsuser', irods_user)

        user_home = imain.get_user_home(irods_user)

        # If all is well, give our local token to this validated user
        local_token, jti = auth.create_token(auth.fill_payload(intuser))
        auth.save_token(auth._user, local_token, jti)

        return self.force_response(
            defined_content={
                'token': local_token,
                'b2safe_user': irods_user,
                'b2safe_home': user_home,
            }
        )


class B2accesProxyEndpoint(EudatEndpoint):
    """
    Allow refreshing current proxy (if invalid)
    using the stored b2access token (if still valid)
    """

    baseuri = '/auth'
    labels = ['eudat', 'b2access']
    depends_on = ['B2ACCESS_APPKEY']
    POST = {
        '/proxy': {
            'custom': {},
            'summary': 'Check and/or refresh current B2ACCESS proxy credentials',
            'responses': {'200': {'description': 'refresh status'}},
        }
    }

    @authentication.required()
    def post(self):

        ##########################
        # get the response
        r = self.init_endpoint()  # only_check_proxy=True)
        if r.errors is not None:
            return self.send_errors(errors=r.errors)

        ##########################
        # verify what happened
        if r.valid_credentials:
            if r.refreshed:
                return {"Expired": "New proxy was generated."}
            else:
                log.debug("Current user does not use a proxy")
                return {"Skipped": "Not using a certificate proxy."}

        return {"Info": "Unknown status."}
