# -*- coding: utf-8 -*-

"""
Take care of authenticatin with External Service with Oauth2 protocol.

Testend against GitHub, then worked off B2ACCESS (EUDAT oauth service)
"""

import os
from flask_oauthlib.client import OAuth
from base64 import b64encode
from restapi.utilities.globals import mem
from restapi.utilities.meta import Meta

from restapi.utilities.logs import log

meta = Meta()

B2ACCESS_MAIN_PORT = 8443
B2ACCESS_CA_PORT = 8445
B2ACCESS_URLS = {
    'development': 'unity.eudat-aai.fz-juelich.de',
    'staging': 'b2access-integration.fz-juelich.de',
    'production': 'b2access.eudat.eu',
}


class ExternalLogins(object):

    _available_services = {}

    def __init__(self, app):

        self.oauth = OAuth()
        self.oauth.init_app(app)
        # Global memory of oauth2 services across the whole server instance:
        # because we may define the external service
        # in different places of the code
        if not self._check_if_services_exist():
            # NOTE: this gets called only at INIT time
            mem.oauth2_services = self.get_oauth2_instances()

        # Recover services for current instance
        # This list will be used from the outside world
        self._available_services = mem.oauth2_services

    @staticmethod
    def _check_if_services_exist():
        return getattr(mem, 'oauth2_services', None) is not None

    def get_oauth2_instances(self):
        """
        Setup every oauth2 instance available through configuration
        """

        services = {}

        # Check if credentials are enabled inside docker env
        if 'B2ACCESS_APPNAME' not in os.environ or 'B2ACCESS_APPKEY' not in os.environ:
            log.verbose("Skipping B2ACCESS Oauth2 service")
            return services

        # Call the service and save it
        try:
            obj = self.b2access()

            # Cycle all the Oauth2 group services
            for name, oauth2 in obj.items():
                if oauth2 is None:
                    log.debug("Skipping failing credentials: B2ACCESS")
                else:
                    services[name] = oauth2
                    log.debug("Created Oauth2 service {}", name)

        except Exception as e:
            log.critical("Unable to request oauth2 service B2ACCESS: {}", e)

        return services

    def b2access(self):

        from restapi.services.detect import Detector as detect

        b2access_vars = detect.load_variables(prefix='b2access_')
        selected_b2access = b2access_vars.get('env')
        if selected_b2access is None:
            return {}

        # load credentials from environment
        key = b2access_vars.get('appname', 'yourappusername')
        secret = b2access_vars.get('appkey', 'yourapppw')

        if secret is None or secret.strip() == '':
            log.info("B2ACCESS credentials not set")
            return {}

        base_url = B2ACCESS_URLS.get(selected_b2access)
        b2access_url = "https://{}:{}".format(base_url, B2ACCESS_MAIN_PORT)
        b2access_ca = "https://{}:{}".format(base_url, B2ACCESS_CA_PORT)

        # SET OTHER URLS
        token_url = b2access_url + '/oauth2/token'
        authorize_url = b2access_url + '/oauth2-as/oauth2-authz'

        # COMMON ARGUMENTS
        arguments = {
            'consumer_key': key,
            'consumer_secret': secret,
            'access_token_url': token_url,
            'authorize_url': authorize_url,
            'request_token_params': {
                'scope': ['USER_PROFILE', 'GENERATE_USER_CERTIFICATE']
            },
            # request_token_url is for oauth1
            'request_token_url': None,
            'access_token_method': 'POST',
        }

        # B2ACCESS main app
        arguments['base_url'] = b2access_url + '/oauth2/'
        b2access_oauth = self.oauth.remote_app('b2access', **arguments)

        # B2ACCESS certification authority app
        arguments['base_url'] = b2access_ca
        b2accessCA = self.oauth.remote_app('b2accessCA', **arguments)

        #####################
        # Decorated session save of the token
        @b2access_oauth.tokengetter
        @b2accessCA.tokengetter
        def get_b2access_oauth_token():
            from flask import session

            return session.get('b2access_token')

        return {
            'b2access': b2access_oauth,
            'b2accessCA': b2accessCA,
            'prod': selected_b2access == 'production',
        }


def decorate_http_request(remote):
    """
    Decorate the OAuth call to access token endpoint,
    injecting the Authorization header.
    """

    old_http_request = remote.http_request

    def new_http_request(uri, headers=None, data=None, method=None):
        response = None
        if not headers:
            headers = {}
        if not headers.get("Authorization"):
            client_id = remote.consumer_key
            client_secret = remote.consumer_secret
            userpass = b64encode(
                str.encode("{}:{}".format(client_id, client_secret))
            ).decode("ascii")
            headers.update({'Authorization': 'Basic {}'.format(userpass,)})
        response = old_http_request(uri, headers=headers, data=data, method=method)

        # TODO: check if we may handle failed B2ACCESS response here
        return response

    remote.http_request = new_http_request
