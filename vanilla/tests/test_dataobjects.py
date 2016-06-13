# -*- coding: utf-8 -*-

"""
Test  dataobjects endpoints
"""

from __future__ import absolute_import

import io
import json
import unittest
import logging
import commons.htmlcodes as hcodes
from restapi.server import create_app
from confs.config import USER, PWD, \
    TEST_HOST, SERVER_PORT, API_URL, AUTH_URL

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'
#logger = get_logger(__name__)
#logger.setLevel(logging.DEBUG)

API_URI = 'http://%s:%s%s' % (TEST_HOST, SERVER_PORT, API_URL)
AUTH_URI = 'http://%s:%s%s' % (TEST_HOST, SERVER_PORT, AUTH_URL)


class TestDataObjects(unittest.TestCase):

    @classmethod
    def setUp(self):
        "set up test fixtures"
        #logger.debug('### Setting up the Flask server ###')
        app = create_app(testing=True)
        self.app = app.test_client()

    @classmethod
    def tearDown(self):
        "tear down test fixtures"
        #logger.debug('### Tearing down the Flask server ###')
        del self.app

    def test_01_get_verify(self):
        """ Test if the Flask server is running and reachable
            and login """

        # Check success
        endpoint = API_URI + '/status'
        r = self.app.get(endpoint)
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

        # Authenitcate
        endpoint = AUTH_URI + '/login'
        #logger.info("*** VERIFY valid credentials")
        r = self.app.post(endpoint,
                          data=json.dumps({'username': USER, 'password': PWD}))
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

        content = json.loads(r.data.decode('utf-8'))
        # Since unittests use class object and not instances
        # This is the only workaround to set a persistent variable
        # self.auth_header does not work
        self.__class__.auth_header = {
            'Authorization': 'Bearer ' + content['Response']['data']['token']}

         # Check failure
        #logger.info("*** VERIFY if invalid endpoint gives Not Found")
        r = self.app.get(API_URI)
        self.assertEqual(r.status_code, hcodes.HTTP_BAD_NOTFOUND)

    def test_02_post_dataobjects(self):
        """ Test file upload: POST """

        # POST dataobject
        endpoint = API_URI + '/dataobjects'
        r = self.app.post(endpoint, data=dict(
                          file=(io.BytesIO(b"this is a test"), 'test.pdf')),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

    def test_03_post_dataobjects_in_specific_collection(self):
        """ Test file upload: POST """
        r = self.app.post(API_URI + '/dataobjects', data=dict(
                          file=(io.BytesIO(b"this is a test"), 'test1.pdf'),
                          collection='/home/guest'))
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

    def test_04_post_large_dataobjects(self):
        """ Test large file upload: POST """
        path = os.path.join('/home/irods', 'img.JPG')
        with open(path, "wb") as f:
            f.seek(100000000)  # 100MB file
            f.write(b"\0")
        r = self.app.post(API_URI + '/dataobjects', data=dict(
                           file=(open(path, 'rb'), 'img.JPG')))
        os.remove(path)
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)  # maybe 201 is more appropriate

    def test_05_get_dataobjects(self):
        """ Test file download: GET """
        deleteURI = os.path.join(API_URI + '/dataobjects',
                                 'test.pdf')
        r = self.app.get(deleteURI, data=dict(collection=('/home/guest')))
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
        self.assertEqual(r.data, b'this is a test')

    def test_06_get_large_dataobjects(self):
        """ Test file download: GET """
        deleteURI = os.path.join(API_URI + '/dataobjects',
                                 'img.JPG')
        r = self.app.get(deleteURI, data=dict(collection=('/home/guest')))
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

    def test_07_post_already_existing_dataobjects(self):
        """ Test file upload with already existsing object: POST """
        r = self.app.post(API_URI + '/dataobjects', data=dict(
                          file=(io.BytesIO(b"this is a test"), 'test.pdf')))
        self.assertEqual(r.status_code, hcodes.HTTP_BAD_REQUEST)  # or 409?
        content = json.loads(r.data.decode('utf-8'))
        error_message = content['Response']['errors']
        #logger.debug(error_message)

    def test_08_delete_dataobjects(self):
        """ Test file delete: DELETE """

        # Obatin the list of objects end delete
        r = self.app.get(API_URI + '/collections')
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
        # is the following correct?
        content = json.loads(r.data.decode('utf-8'))
        # why each element inside data is a list with only 1 element?
        collection = content['Response']['data'][0][0][:-1]
        # I have to remove the zone part.. this should probably be discussed
        collection = '/' + collection.split('/', 2)[2]
        for idx, obj in enumerate(content['Response']['data']):
            if idx == 0:
                continue
            deleteURI = os.path.join(API_URI + '/dataobjects',
                                     obj[0])
            r = self.app.delete(deleteURI, data=dict(collection=(collection)))
            self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

    def test_09_post_dataobjects_in_non_existing_collection(self):
        """ Test file upload in a non existing collection: POST """
        r = self.app.post(API_URI + '/dataobjects', data=dict(
                         collection=('/home/wrong/guest'),
                         file=(io.BytesIO(b"this is a test"), 'test.pdf')))
        self.assertEqual(r.status_code, hcodes.HTTP_BAD_REQUEST)  # or 409?
        content = json.loads(r.data.decode('utf-8'))
        error_message = content['Response']['errors'][0]['iRODS']
        self.assertIn('collection does not exist', error_message)

    def test_10_get_non_exising_dataobjects(self):
        """ Test file download of a non existing object: GET """
        deleteURI = os.path.join(API_URI + '/dataobjects',
                                 'test.pdf')
        r = self.app.get(deleteURI, data=dict(collection=('/home/guest')))
        self.assertEqual(r.status_code, hcodes.HTTP_BAD_REQUEST)  # or 404?
        content = json.loads(r.data.decode('utf-8'))
        error_message = content['Response']['errors'][0]['iRODS']
        self.assertIn('does not exist on the specified path', error_message)

    def test_11_get_dataobjects_in_non_exising_collection(self):
        """ Test file download in a non existing collection: GET """
        delURI = os.path.join(API_URI + '/dataobjects',
                              'test.pdf')
        r = self.app.get(delURI, data=dict(collection=('/home/wrong/guest')))
        self.assertEqual(r.status_code, hcodes.HTTP_BAD_REQUEST)  # or 404?
        content = json.loads(r.data.decode('utf-8'))
        error_message = content['Response']['errors'][0]['iRODS']
        self.assertIn('does not exist on the specified path', error_message)
