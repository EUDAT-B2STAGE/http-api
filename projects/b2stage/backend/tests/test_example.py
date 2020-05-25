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


class TestDataObjects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        log.info('### Setting up flask server ###')
        app = create_app(testing=True)
        cls.app = app.test_client()

    @classmethod
    def tearDownClass(cls):
        log.info('### Tearing down the flask server ###')
