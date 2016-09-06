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

#####################
logger.critical("DataObjects: " +
                "No tests available until specs implemented")
import time
time.sleep(2)
logger.info("Running base tests:\n\n")
time.sleep(1)
#####################

# API_URI = 'http://%s:%s%s' % (TEST_HOST, SERVER_PORT, API_URL)
# AUTH_URI = 'http://%s:%s%s' % (TEST_HOST, SERVER_PORT, AUTH_URL)


# class TestDataObjects(unittest.TestCase):

#     @classmethod
#     def setUpClass(cls):
#         logger.info('### Setting up flask server ###')
#         app = create_app(testing_mode=True)
#         cls.app = app.test_client()

#         r = cls.app.post(
#             AUTH_URI + '/login',
#             data=json.dumps({'username': USER, 'password': PWD}))
#         content = json.loads(r.data.decode('utf-8'))
#         cls.auth_header = {
#             'Authorization': 'Bearer ' + content['Response']['data']['token']}

#     @classmethod
#     def tearDownClass(cls):
#         logger.info('### Tearing down the flask server ###')
#         del cls.app

#         # Tokens clean up
#         logger.debug("Cleaned up invalid tokens")
#         from restapi.resources.services.neo4j.graph import MyGraph
#         MyGraph().clean_pending_tokens()

#     def test_01_post_dataobjects(self):
#         """ Test file upload: POST """

#         # POST dataobject
#         endpoint = API_URI + '/dataobjects'
#         r = self.app.post(endpoint, data=dict(
#                           file=(io.BytesIO(b"this is a test"), 'test.pdf')),
#                           headers=self.auth_header)
#         self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

#     def test_02_post_dataobjects_in_specific_collection(self):
#         """ Test file upload: POST """

#         URI = API_URI + '/collections'
#         # Create the collection
#         r = self.app.post(URI, headers=self.auth_header,
#                           data=dict(collection='test', force='True'))
#         self.assertEqual(r.status_code, hcodes.HTTP_OK_CREATED)

#         URI = API_URI + '/dataobjects'

#         # Absolute path
#         r = self.app.post(
#             URI, headers=self.auth_header,
#             data=dict(
#                 file=(io.BytesIO(b"this is a test"), 'test1.pdf'),
#                 collection='/home/guest/test'))
#         self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

#         # Relative path
#         r = self.app.post(
#             URI, headers=self.auth_header,
#             data=dict(
#                 file=(io.BytesIO(b"this is a test"), 'test2.pdf'),
#                 collection='test', force='True'))
#         self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

#     def test_03_post_large_dataobjects(self):
#         """ Test large file upload: POST """
#         path = os.path.join('/home/irods', 'img.JPG')
#         with open(path, "wb") as f:
#             f.seek(100000000)  # 100MB file
#             f.write(b"\0")
#         r = self.app.post(API_URI + '/dataobjects', data=dict(
#                           file=(open(path, 'rb'), 'img.JPG')),
#                           headers=self.auth_header)
#         os.remove(path)
#     ## maybe 201 is more appropriate?
#         self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

#         content = json.loads(r.data.decode('utf-8'))
#         self.__class__.large = content['Response']['data']['id']

#     def test_04_post_overwrite_dataobjects(self):
#         """ Test file upload: POST """

#         # POST dataobject
#         endpoint = API_URI + '/dataobjects'
#         r = self.app.post(endpoint, data=dict(force='True',
#                           file=(io.BytesIO(b"a test again"), 'test.pdf')),
#                           headers=self.auth_header)
#         self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

#         content = json.loads(r.data.decode('utf-8'))
#         self.__class__.small = content['Response']['data']['id']

#     def test_05_get_dataobjects(self):
#         """ Test file download: GET """

#         objURI = os.path.join(API_URI, 'dataobjects', self.__class__.small)
#         r = self.app.get(objURI, headers=self.auth_header)
#         self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
#         # Verify file content
#         self.assertEqual(r.data, b'a test again')

#     def test_06_get_large_dataobjects(self):
#         """ Test file download: GET """
#         objURI = os.path.join(API_URI, 'dataobjects', self.__class__.large)
#         r = self.app.get(objURI, headers=self.auth_header)
#         self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

#     def test_07_post_already_existing_dataobjects(self):
#         """ Test file upload with already existsing object: POST """
#         r = self.app.post(
#             API_URI + '/dataobjects',
#             headers=self.auth_header,
#             data=dict(file=(io.BytesIO(b"this is a test"), 'test.pdf')))
#         # content = json.loads(r.data.decode('utf-8'))
#         # error_message = content['Response']['errors']
#         # logger.debug(error_message)
#         self.assertEqual(r.status_code, hcodes.HTTP_BAD_REQUEST)  # or 409?

# ## // TO FIX:
# # If tests fails before the next method,
# # you will find your self with data already existing on irods
# # which will lead to errors also when tests are good

# # Maybe we could add a method which finds data and removes it
# # at 'init time' of the class.

#     def test_08_delete_dataobjects(self):
#         """ Test file delete: DELETE """

#         URI = os.path.join(API_URI, 'dataobjects')

#         # Obtain the list of objects end delete
#         r = self.app.get(URI, headers=self.auth_header)
#         self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
#         content = json.loads(r.data.decode('utf-8'))

#         # Find the path
#         data = content['Response']['data']['content']
#         for obj in data:
#             deleteURI = os.path.join(URI, obj['id'])
#             r = self.app.delete(deleteURI, headers=self.auth_header)
#             self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)

#     def test_09_delete_nonexisting_dataobjects(self):
#         """ Test fake file delete: DELETE """

#         URI = os.path.join(API_URI, 'dataobjects', 'NonExistingUUID')
#         r = self.app.get(URI, headers=self.auth_header)
#         self.assertEqual(r.status_code, hcodes.HTTP_SERVER_ERROR)

#     def test_10_post_dataobjects_in_non_existing_collection(self):
#         """ Test file upload in a non existing collection: POST """

#         URI = os.path.join(API_URI, 'dataobjects')
#         r = self.app.post(
#             URI, headers=self.auth_header,
#             data=dict(collection=('/home/wrong/path'),
#                       file=(io.BytesIO(b"this is a test"), 'test.pdf')))
#         self.assertEqual(r.status_code, hcodes.HTTP_BAD_REQUEST)  # or 409?
#         content = json.loads(r.data.decode('utf-8'))
#         error_message = content['Response']['errors'][0]['iRODS']
#         self.assertIn('collection does not exist', error_message)

#     def test_11_get_non_exising_dataobjects(self):
#         """ Test file download of a non existing object: GET """

#         filename = 'test.pdf'
#         URI = os.path.join(API_URI, 'dataobjects', filename)

#         r = self.app.get(
#             URI, headers=self.auth_header,
#             data=dict(collection=('/home/guest')))
#         self.assertEqual(r.status_code, hcodes.HTTP_SERVER_ERROR)  # or 404?

#         content = json.loads(r.data.decode('utf-8'))
#         error_messages = content['Response']['errors'].pop()
#         self.assertIn('Not found.', error_messages[filename])
