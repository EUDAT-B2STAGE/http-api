# # -*- coding: utf-8 -*-


"""
THIS STUFF IS BASED ON NOSE2 -> TO BE REMOVED!!!
"""

import unittest
import json
# import logging
# from restapi import __package__ as current_package
from restapi.server import create_app
from restapi.tests import get_content_from_response
from restapi.services.authentication import BaseAuthentication as ba
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log
#  , set_global_log_level
from restapi.tests import API_URI, AUTH_URI

# To change UNITTEST debugging level
# TEST_DEBUGGING_LEVEL = logging.DEBUG
# set_global_log_level(current_package, TEST_DEBUGGING_LEVEL)


class RestTestsBase(unittest.TestCase):

    _api_uri = API_URI
    _auth_uri = AUTH_URI
    _hcodes = hcodes

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

    def setUp(self):
        """
        Note: in this base tests,
        I also want to check if i can run multiple Flask applications.

        Thi is why i prefer setUp on setUpClass
        """
        log.debug('### Setting up the Flask server ###')
        app = create_app(testing_mode=True)
        self.app = app.test_client()

        # Auth init from base/custom config
        ba.myinit()
        self._username = ba.default_user
        self._password = ba.default_password

    def tearDown(self):
        log.debug('### Tearing down the Flask server ###')
        del self.app

    def get_service_handler(self, service_name):
        from restapi.services.detect import detector

        ExtClass = detector.services_classes.get(service_name)
        return ExtClass().get_instance()

    def get_content(self, response, return_errors=False):
        content, err = get_content_from_response(response)

        # Since unittests use class object and not instances
        # This is the only workaround to set a persistent variable:
        # abuse of the __class__ property

        if return_errors:
            return err
        else:
            return content


#####################
class RestTestsAuthenticatedBase(RestTestsBase):
    def save_token(self, token, suffix=None):

        if suffix is None:
            suffix = ''
        else:
            suffix = '_' + suffix

        key = 'bearer_token' + suffix
        setattr(self.__class__, key, token)

        key = 'auth_header' + suffix
        setattr(self.__class__, key, {'Authorization': 'Bearer {}'.format(token)})

    def setUp(self):

        # Call father's method
        super().setUp()

        log.info("### Creating a test token ###")
        endpoint = self._auth_uri + '/login'
        credentials = json.dumps(
            {'username': self._username, 'password': self._password}
        )
        r = self.app.post(endpoint, data=credentials)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        content = self.get_content(r)
        self.save_token(content.get('token'))

    def tearDown(self):

        # Token clean up
        log.debug('### Cleaning token ###')
        ep = self._auth_uri + '/tokens'
        # Recover current token id
        r = self.app.get(ep, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        content = self.get_content(r)
        for element in content:
            if element.get('token') == self.__class__.bearer_token:
                # delete only current token
                ep += '/' + element.get('id')
                rdel = self.app.delete(ep, headers=self.__class__.auth_header)
                self.assertEqual(rdel.status_code, self._hcodes.HTTP_OK_NORESPONSE)

        # The end
        super().tearDown()
        log.info("Completed one method to test\n\n")
