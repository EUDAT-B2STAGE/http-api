# -*- coding: utf-8 -*-

"""
Test  dataobjects endpoints
"""

import unittest
from restapi.server import create_app


__author__ = 'Roberto Mucci (r.mucci@cineca.it)'


class TestDataObjects(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        "set up test fixtures"
        print('### Setting up flask server ###')
        app = create_app()
        app.config['TESTING'] = True
        self.app = app.test_client()

    @classmethod
    def tearDownClass(self):
        "tear down test fixtures"
        print('### Tearing down the flask server ###')

    def test_01_empty(self):
        pass
