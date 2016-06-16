# -*- coding: utf-8 -*-

"""
Test  dataobjects endpoints
"""

# import io
# import os
# import json
import unittest
from restapi.server import create_app


__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


class TestCollections(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        "set up test fixtures"
        print('### Setting up flask server ###')
        app = create_app(testing=True)
        # app.config['TESTING'] = True
        self.app = app.test_client()

    @classmethod
    def tearDownClass(self):
        "tear down test fixtures"
        print('### Tearing down the flask server ###')

    # def test_01_get_status(self)
    #     """ Test that the flask server is running and reachable"""

    #     r = self.app.get('http://localhost:8080/api/status')
    #     self.assertEqual(r.status_code, 200)
