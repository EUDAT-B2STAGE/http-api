# -*- coding: utf-8 -*-

"""
Test collection endpoints.

Run single test:
nose2 test.custom.test_collections.TestCollections.test_01_get_collections

"""

from __future__ import absolute_import

import os
import json
import unittest
import commons.htmlcodes as hcodes
from restapi.server import create_app
from restapi.confs.config import USER, PWD, \
    TEST_HOST, SERVER_PORT, API_URL, AUTH_URL

from commons.logs import get_logger
from commons import myself

__author__ = myself

logger = get_logger(__name__, True)

API_URI = 'http://%s:%s%s' % (TEST_HOST, SERVER_PORT, API_URL)
AUTH_URI = 'http://%s:%s%s' % (TEST_HOST, SERVER_PORT, AUTH_URL)


class TestCollections(unittest.TestCase):

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

        # Tokens clean up
        logger.debug("Cleaned up invalid tokens")
        from restapi.resources.services.neo4j.graph import MyGraph
        MyGraph().clean_pending_tokens()

    def test_01_get_collections(self):
        """ Test """

        URI = os.path.join(API_URI, 'collections')
        r = self.app.get(URI, headers=self.auth_header)
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
        out = json.loads(r.data.decode('utf-8'))
        self.assertIsInstance(out['Response']['data']['content'], list)
