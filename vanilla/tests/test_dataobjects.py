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


class TestDataObjects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        logger.info('### Setting up flask server ###')
        app = create_app(testing=True)
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

    def test_01_post_dataobjects(self):
        """ Test file upload: POST """

        # POST dataobject
        endpoint = API_URI + '/dataobjects'
        r = self.app.post(endpoint, data=dict(
                          file=(io.BytesIO(b"this is a test"), 'test.pdf')),
                          headers=self.auth_header)
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

    def test_02_post_dataobjects_in_specific_collection(self):
        """ Test file upload: POST """
        r = self.app.post(API_URI + '/dataobjects', data=dict(
                          file=(io.BytesIO(b"this is a test"), 'test1.pdf'),
                          collection='/home/guest'),
                          headers=self.auth_header)
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

    def test_03_post_large_dataobjects(self):
        """ Test large file upload: POST """
        path = os.path.join('/home/irods', 'img.JPG')
        with open(path, "wb") as f:
            f.seek(100000000)  # 100MB file
            f.write(b"\0")
        r = self.app.post(API_URI + '/dataobjects', data=dict(
                          file=(open(path, 'rb'), 'img.JPG')),
                          headers=self.auth_header)
        os.remove(path)
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
        # maybe 201 is more appropriate

    def test_04_get_dataobjects(self):
        """ Test file download: GET """
        objURI = os.path.join(API_URI + '/dataobjects', 'test.pdf')
        r = self.app.get(
            objURI, headers=self.auth_header,
            data=dict(collection=('/home/guest')))
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
        self.assertEqual(r.data, b'this is a test')

    def test_05_get_large_dataobjects(self):
        """ Test file download: GET """
        objURI = os.path.join(API_URI + '/dataobjects', 'img.JPG')
        r = self.app.get(
            objURI, headers=self.auth_header,
            data=dict(collection=('/home/guest')))
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

    def test_06_post_already_existing_dataobjects(self):
        """ Test file upload with already existsing object: POST """
        r = self.app.post(
            API_URI + '/dataobjects',
            headers=self.auth_header,
            data=dict(file=(io.BytesIO(b"this is a test"), 'test.pdf')))
        # content = json.loads(r.data.decode('utf-8'))
        # error_message = content['Response']['errors']
        # logger.debug(error_message)
        self.assertEqual(r.status_code, hcodes.HTTP_BAD_REQUEST)  # or 409?

## // TO FIX:
# If tests fails before the next method,
# you will find your self with data already existing on irods
# which will lead to errors also when tests are good

# Maybe we could add a method which finds data and removes it
# at 'init time' of the class.

    @staticmethod
    def get_first_collection_from_many(data):
        """ Parse API response to get a single element collection """

        # element = data[list(data.keys()).pop()]
        element = data.pop()['attributes']
        attributes = element.get(list(element.keys()).pop())
        path = attributes['path']
        return path.strip('/')[path.find('/', 1) - 1:]

    def test_07_delete_dataobjects(self):
        """ Test file delete: DELETE """

        # Obatin the list of objects end delete
        r = self.app.get(API_URI + '/collections', headers=self.auth_header)
        self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
        # is the following correct?
        content = json.loads(r.data.decode('utf-8'))

        # Find the path
        data = content['Response']['data']['content']
        collection = None
        try:
            collection = self.get_first_collection_from_many(data.copy())
        except Exception as e:
            logger.critical("Unknown response content format")
            raise e

        print("TEST", data)
        for _, obj in data[0]['attributes'].items():
            deleteURI = os.path.join(API_URI + '/dataobjects', obj['name'])
            r = self.app.delete(
                deleteURI, headers=self.auth_header,
                data=dict(collection=(collection)))
            self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

## // TO FIX:
# We should also test the removal of an object that does not exist

    def test_08_post_dataobjects_in_non_existing_collection(self):
        """ Test file upload in a non existing collection: POST """
        r = self.app.post(
            API_URI + '/dataobjects', headers=self.auth_header,
            data=dict(collection=('/home/wrong/guest'),
                      file=(io.BytesIO(b"this is a test"), 'test.pdf')))
        self.assertEqual(r.status_code, hcodes.HTTP_BAD_REQUEST)  # or 409?
        content = json.loads(r.data.decode('utf-8'))
        error_message = content['Response']['errors'][0]['iRODS']
        self.assertIn('collection does not exist', error_message)

    def test_09_get_non_exising_dataobjects(self):
        """ Test file download of a non existing object: GET """
        URI = os.path.join(API_URI + '/dataobjects', 'test.pdf')
        r = self.app.get(
            URI, headers=self.auth_header,
            data=dict(collection=('/home/guest')))
        self.assertEqual(r.status_code, hcodes.HTTP_BAD_REQUEST)  # or 404?
        content = json.loads(r.data.decode('utf-8'))
        error_message = content['Response']['errors'][0]['iRODS']
        self.assertIn('does not exist on the specified path', error_message)

    def test_10_get_dataobjects_in_non_exising_collection(self):
        """ Test file download in a non existing collection: GET """
        URI = os.path.join(API_URI + '/dataobjects', 'test.pdf')
        r = self.app.get(
            URI, headers=self.auth_header,
            data=dict(collection=('/home/wrong/guest')))
        self.assertEqual(r.status_code, hcodes.HTTP_BAD_REQUEST)  # or 404?
        content = json.loads(r.data.decode('utf-8'))
        error_message = content['Response']['errors'][0]['iRODS']
        self.assertIn('does not exist on the specified path', error_message)
