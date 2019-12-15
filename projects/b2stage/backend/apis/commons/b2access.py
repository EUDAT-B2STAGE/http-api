# -*- coding: utf-8 -*-

"""
B2ACCESS utilities
"""

import json
import requests
from flask import session
from base64 import b64encode
from datetime import datetime as dt
from flask_oauthlib.client import OAuthResponse
from urllib3.exceptions import HTTPError

from restapi.rest.definition import EndpointResource
from restapi.services.oauth2clients import decorate_http_request

from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log

# 12 h
IRODS_CONNECTION_TTL = 43200


class B2accessUtilities(EndpointResource):
    def get_main_irods_connection(self):
        # NOTE: Main API user is the key to let this happen
        return self.get_service_instance(
            service_name='irods', cache_expiration=IRODS_CONNECTION_TTL
        )

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
        b2a_refresh_token = None

        try:
            resp = b2access.authorized_response()
        except json.decoder.JSONDecodeError as e:
            log.critical("B2ACCESS empty:\n%s\nCheck your app credentials", e)
            return (
                b2a_token,
                b2a_refresh_token,
                'Server misconfiguration: oauth2 failed',
            )
        except Exception as e:
            # raise e  # DEBUG
            log.critical("Failed to get authorized in B2ACCESS: %s", e)
            return (b2a_token, b2a_refresh_token, 'B2ACCESS OAUTH2 denied: %s' % e)
        if resp is None:
            return (b2a_token, b2a_refresh_token, 'B2ACCESS denied: unknown error')

        b2a_token = resp.get('access_token')
        if b2a_token is None:
            log.critical("No token received")
            return (b2a_token, 'B2ACCESS: empty token')
        log.info("Received token: '%s'" % b2a_token)

        b2a_refresh_token = resp.get('refresh_token')
        log.info("Received refresh token: '%s'" % b2a_refresh_token)
        return (b2a_token, b2a_refresh_token, tuple())

    def get_b2access_user_info(
        self, auth, b2access, b2access_token, b2access_refresh_token
    ):
        """ Get user info from current b2access token """

        # To use the b2access token with oauth2 client
        # We have to save it into session
        session['b2access_token'] = (b2access_token, '')

        # Calling with the oauth2 client
        b2access_user = b2access.get('userinfo')

        error = True
        if b2access_user is None:
            errstring = "Empty response from B2ACCESS"
        elif not isinstance(b2access_user, OAuthResponse):
            errstring = "Invalid response from B2ACCESS"
        elif b2access_user.status > hcodes.HTTP_TRESHOLD:
            log.error("Bad status: %s" % str(b2access_user._resp))
            if b2access_user.status == hcodes.HTTP_BAD_UNAUTHORIZED:
                errstring = "B2ACCESS token obtained is unauthorized..."
            else:
                errstring = (
                    "B2ACCESS token obtained failed with %s" % b2access_user.status
                )
        elif isinstance(b2access_user._resp, HTTPError):
            errstring = "Error from B2ACCESS: %s" % b2access_user._resp
        elif not hasattr(b2access_user, 'data'):
            errstring = "Authorized response is invalid (missing data)"
        elif b2access_user.data.get('email') is None:
            errstring = "Authorized response is invalid (missing email)"
        else:
            error = False

        if error:
            return None, None, errstring

        # Attributes you find: http://j.mp/b2access_profile_attributes

        # Store b2access information inside the db
        intuser, extuser = auth.store_oauth2_user(
            "b2access", b2access_user, b2access_token, b2access_refresh_token
        )
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

        return b2access_user, intuser, extuser

    def refresh_b2access_token(self, auth, b2access_user, b2access, refresh_token):
        """
            curl -X POST
                 -u 'myClientID':'myClientSecret'
                 -d '
                     grant_type=refresh_token&
                     refresh_token=myRefreshToken&
                     scope=USER_PROFILE'
                  'https://unity.eudat-aai.fz-juelich.de/oauth2/token'

            OR -H "Authorization Basic base64(client_id:client_secret)" instead of -u
        """

        client_id = b2access._consumer_key
        client_secret = b2access._consumer_secret

        refresh_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": 'USER_PROFILE',
        }
        auth_hash = b64encode(str.encode("%s:%s" % (client_id, client_secret))).decode(
            "ascii"
        )
        headers = {'Authorization': 'Basic %s' % auth_hash}

        resp = requests.post(
            b2access.access_token_url, data=refresh_data, headers=headers
        )
        resp = resp.json()

        access_token = resp['access_token']

        # Store b2access information inside the db
        intuser, extuser = auth.store_oauth2_user(
            "b2access", b2access_user, access_token, refresh_token
        )
        # In case of error this account already existed...
        if intuser is None:
            log.error("Failed to store new access token")
            return None

        log.info("New access token = %s", access_token)

        return access_token

    def get_irods_user_from_b2access(self, icom, email):
        """ EUDAT RULE for b2access-to-b2safe user mapping """

        inputs = {}
        body = """
            EUDATGetPAMusers(*json_map);
            writeLine("stdout", *json_map);
        """

        rule_output = icom.rule('get_pid', body, inputs, output=True)
        try:
            rule_output = json.loads(rule_output)
        except BaseException:
            log.error("Unable to convert rule output as json: %s", rule_output)
            return None

        for user in rule_output:
            if email in rule_output[user]:
                return user
        return None
