# -*- coding: utf-8 -*-

"""
Test dataobjects endpoints

Run single test:
nose2 test.custom.test_dataobjects.TestDataObjects.test_07_delete_dataobjects

"""

from __future__ import absolute_import

import io
import os
import json
import unittest
import commons.htmlcodes as hcodes
from restapi.server import create_app
from restapi.confs.config import USER, PWD, \
    TEST_HOST, SERVER_PORT, API_URL, AUTH_URL

from commons.logs import get_logger

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

logger = get_logger(__name__, True)

API_URI = 'http://%s:%s%s' % (TEST_HOST, SERVER_PORT, API_URL)
AUTH_URI = 'http://%s:%s%s' % (TEST_HOST, SERVER_PORT, AUTH_URL)


class TestEntities(unittest.TestCase):

    _main_endpoint = '/entities'

    @classmethod
    def setUpClass(cls):
        logger.info('### Setting up flask server ###')
        app = create_app(testing_mode=True)
        cls.app = app.test_client()

        r = cls.app.post(
            AUTH_URI + '/login',
            data=json.dumps({'username': USER, 'password': PWD}))
        content = json.loads(r.data.decode('utf-8'))
        cls.auth_header = {
            'Authorization': 'Bearer ' + content['Response']['data']['token']}

    @classmethod
    def tearDownClass(cls):
        logger.info('### Tearing down the flask server ###')
        del cls.app

        # # Tokens clean up
        # logger.debug("Cleaned up invalid tokens")
        # from restapi.resources.services.neo4j.graph import MyGraph
        # MyGraph().clean_pending_tokens()

    def test_01_post_digitalentity(self):
        """ Test file upload: POST """

        # POST dataobject
        endpoint = API_URI + self._main_endpoint
        r = self.app.post(
            endpoint,
            data=dict(
                file=(io.BytesIO(b"this is a test"), 'test.pdf'),
                force=True
            ), headers=self.auth_header)
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
