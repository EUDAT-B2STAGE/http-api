# -*- coding: utf-8 -*-

"""
Test  dataobjects endpoints
"""

# import io
# import os
# import json
import unittest
from restapi.server import create_app
from restapi.utilities.logs import log

__author__ = "Paolo D'Onorio De Meo (GitHub@pdonorio)"

# API_URI = 'http://%s:%s%s' % (TEST_HOST, SERVER_PORT, API_URL)
# AUTH_URI = 'http://%s:%s%s' % (TEST_HOST, SERVER_PORT, AUTH_URL)


class TestDataObjects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        log.info('### Setting up flask server ###')
        app = create_app(testing=True)
        cls.app = app.test_client()

        # r = cls.app.post(
        #     AUTH_URI + '/login',
        #     data=json.dumps({'username': USER, 'password': PWD}))
        # content = json.loads(r.data.decode('utf-8'))
        # token = content['Response']['data']['token']
        # cls.auth_header = {
        #     'Authorization': 'Bearer ' + token}

    @classmethod
    def tearDownClass(cls):
        log.info('### Tearing down the flask server ###')

    # def test_01_get_someendpoint(self):

    #     log.debug("Testing a random endpoint")
    #     r = self.app.get(AUTH_URI + '/profile', headers=self.auth_header)
    #     self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
