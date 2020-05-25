# # -*- coding: utf-8 -*-
import unittest
import json
from restapi.server import create_app
from restapi.services.authentication import BaseAuthentication as ba
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log
from restapi.tests import API_URI, AUTH_URI


class RestTestsAuthenticatedBase(unittest.TestCase):

    """
    HOW TO

    # initialization logic for the test suite declared in the test module
    # code that is executed before all tests in one test run
    @classmethod
    def setUpClass(cls):
        pass

    # clean up logic for the test suite declared in the test module
    # code that is executed after all tests in one test run
    @classmethod
    def tearDownClass(cls):
        pass

    # initialization logic
    # code that is executed before each test
    def setUp(self):
        pass

    # clean up logic
    # code that is executed after each test
    def tearDown(self):
        pass
    """

    _api_uri = API_URI
    _auth_uri = AUTH_URI
    _hcodes = hcodes

    def setUp(self):

        log.debug('### Setting up the Flask server ###')
        app = create_app(testing_mode=True)
        self.app = app.test_client()

        # Auth init from base/custom config
        ba.load_default_user()

        log.info("### Creating a test token ###")
        endpoint = self._auth_uri + '/login'
        credentials = {
            'username': ba.default_user,
            'password': ba.default_password
        }
        r = self.app.post(endpoint, data=credentials)
        assert r.status_code == self._hcodes.HTTP_OK_BASIC
        # content = self.get_content(r)
        # self.save_token(content.get('token'))
        token = self.get_content(r)
        self.save_token(token)

    def tearDown(self):

        # Token clean up
        log.debug('### Cleaning token ###')
        ep = self._auth_uri + '/tokens'
        # Recover current token id
        r = self.app.get(ep, headers=self.__class__.auth_header)
        assert r.status_code == self._hcodes.HTTP_OK_BASIC
        content = self.get_content(r)
        for element in content:
            if element.get('token') == self.__class__.bearer_token:
                # delete only current token
                ep += '/' + element.get('id')
                rdel = self.app.delete(ep, headers=self.__class__.auth_header)
                assert rdel.status_code == self._hcodes.HTTP_OK_NORESPONSE

        # The end
        log.debug('### Tearing down the Flask server ###')
        del self.app

    def save_token(self, token, suffix=None):

        if suffix is None:
            suffix = ''
        else:
            suffix = '_' + suffix

        key = 'bearer_token' + suffix
        setattr(self.__class__, key, token)

        key = 'auth_header' + suffix
        setattr(self.__class__, key, {'Authorization': 'Bearer {}'.format(token)})

    def get_content(self, http_out):

        response = None

        try:
            response = json.loads(http_out.get_data().decode())
        except Exception as e:
            log.error("Failed to load response:\n{}", e)
            raise ValueError(
                "Malformed response: {}".format(http_out)
            )

        return response
