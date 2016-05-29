# -*- coding: utf-8 -*-

"""
Test  dataobjects endpoints
"""

# import io
# import os
# import json
import unittest
from restapi.server import create_app


__author__ = "Paolo D'Onorio De Meo (GitHub@pdonorio)"


class TestDataObjects(unittest.TestCase):

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

    # def test_02_post_dataobjects(self):
    #     """ Test file upload: POST """
    #     # I need to understand who to reapeat the upload test, since
    #     # overwrite is not allowed
    #     r = self.app.post('http://localhost:8080/api/dataobjects', data=dict(
    #                      file=(io.BytesIO(b"this is a test"),
    #                       'test.pdf')))
    #     self.assertEqual(r.status_code, 200)  # maybe 201 is more appropriate

    # def test_03_post_dataobjects_in_specific_collection(self):
    #     """ Test file upload: POST """
    #     # I need to understand who to reapeat the upload test, since
    #     # overwrite is not allowed
    #     r = self.app.post('http://localhost:8080/api/dataobjects', data=dict(
    #                      file=(io.BytesIO(b"this is a test"),
    #                       'test1.pdf'), collection='/home/guest'))
    #     self.assertEqual(r.status_code, 200)  # maybe 201 is more appropriate


    # def test_04_post_large_dataobjects(self):
    #     """ Test large file upload: POST """
    #     path = os.path.join('/home/irods', 'img.JPG')
    #     with open(path, "wb") as f:
    #         f.seek(100000000)  # 100MB file
    #         f.write(b"\0")
    #     r = self.app.post('http://localhost:8080/api/dataobjects', data=dict(
    #                      file=(open(path, 'rb'), 'img.JPG')))
    #     os.remove(path)
    #     self.assertEqual(r.status_code, 200)  # maybe 201 is more appropriate

    # def test_05_get_dataobjects(self):
    #     """ Test file download: GET """
    #     deleteURI = os.path.join('http://localhost:8080/api/dataobjects',
    #                              'test.pdf')
    #     r = self.app.get(deleteURI, data=dict(collection=('/home/guest')))
    #     self.assertEqual(r.status_code, 200)
    #     self.assertEqual(r.data, b'this is a test')

    # def test_06_get_large_dataobjects(self):
    #     """ Test file download: GET """
    #     deleteURI = os.path.join('http://localhost:8080/api/dataobjects',
    #                              'img.JPG')
    #     r = self.app.get(deleteURI, data=dict(collection=('/home/guest')))
    #     self.assertEqual(r.status_code, 200)

    # def test_07_post_already_existing_dataobjects(self):
    #     """ Test file upload with already existsing object: POST """
    #     r = self.app.post('http://localhost:8080/api/dataobjects', data=dict(
    #                      file=(io.BytesIO(b"this is a test"),
    #                       'test.pdf')))
    #     self.assertEqual(r.status_code, 400)  # or 409?
    #     content = json.loads(r.data.decode('utf-8'))
    #     error_message = content['Response']['errors']
    #     print(error_message)

    # def test_08_delete_dataobjects(self):
    #     """ Test file delete: DELETE """

    #     # Obatin the list of objects end delete
    #     r = self.app.get('http://localhost:8080/api/collections')
    #     self.assertEqual(r.status_code, 200)
    #     # is the following correct?
    #     content = json.loads(r.data.decode('utf-8'))
    #     # why each element inside data is a list with only 1 element?
    #     collection = content['Response']['data'][0][0][:-1]
    #     # I have to remove the zone part.. this should probably be discussed
    #     collection = '/' + collection.split('/', 2)[2]
    #     for idx, obj in enumerate(content['Response']['data']):
    #         if idx == 0:
    #             continue
    #         deleteURI = os.path.join('http://localhost:8080/api/dataobjects',
    #                                  obj[0])
    #         r = self.app.delete(deleteURI, data=dict(collection=(collection)))
    #         self.assertEqual(r.status_code, 200)

    # def test_09_post_dataobjects_in_non_existing_collection(self):
    #     """ Test file upload in a non existing collection: POST """
    #     r = self.app.post('http://localhost:8080/api/dataobjects', data=dict(
    #                      collection=('/home/wrong/guest'),
    #                      file=(io.BytesIO(b"this is a test"), 'test.pdf')))
    #     self.assertEqual(r.status_code, 400)  # or 409?
    #     content = json.loads(r.data.decode('utf-8'))
    #     error_message = content['Response']['errors'][0]['iRODS']
    #     self.assertIn('collection does not exist', error_message)

    # def test_10_get_non_exising_dataobjects(self):
    #     """ Test file download of a non existing object: GET """
    #     deleteURI = os.path.join('http://localhost:8080/api/dataobjects',
    #                              'test.pdf')
    #     r = self.app.get(deleteURI, data=dict(collection=('/home/guest')))
    #     self.assertEqual(r.status_code, 400)  # or 404?
    #     content = json.loads(r.data.decode('utf-8'))
    #     error_message = content['Response']['errors'][0]['iRODS']
    #     self.assertIn('does not exist on the specified path', error_message)

    # def test_11_get_dataobjects_in_non_exising_collection(self):
    #     """ Test file download in a non existing collection: GET """
    #     delURI = os.path.join('http://localhost:8080/api/dataobjects',
    #                           'test.pdf')
    #     r = self.app.get(delURI, data=dict(collection=('/home/wrong/guest')))
    #     self.assertEqual(r.status_code, 400)  # or 404?
    #     content = json.loads(r.data.decode('utf-8'))
    #     error_message = content['Response']['errors'][0]['iRODS']
    #     self.assertIn('does not exist on the specified path', error_message)
