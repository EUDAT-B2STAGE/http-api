# -*- coding: utf-8 -*-

"""
Test dataobjects endpoints

Run single test:
nose2 test.custom.test_dataobjects.TestDataObjects.test_07_delete_dataobjects
"""

from __future__ import absolute_import

import io
from restapi.jsonify import json
from .. import RestTestsAuthenticatedBase
from commons.logs import get_logger

__author__ = 'Roberto Mucci (r.mucci@cineca.it)'

logger = get_logger(__name__, True)


class TestDigitalObjects(RestTestsAuthenticatedBase):

    _main_endpoint = '/namespace'
    _irods_path = '/tempZone/home/guest/test'
    _invalid_irods_path = '/tempZone/home/x/guest/test'
    _test_filename = 'test.pdf'

    def test_01_POST_create_test_directory(self):
        """ Test directory creation: POST """

        logger.info('*** Testing POST')
        # Create a directory
        endpoint = self._api_uri + self._main_endpoint
        r = self.app.post(endpoint, data=dict(path=self._irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Overwrite a directory
        params = json.dumps(dict({'force': True, 'path': self._irods_path}))
        r = self.app.post(endpoint, data=params,
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Overwrite a directory w/o force flag
        r = self.app.post(endpoint, data=dict(path=self._irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)

        # Create a directory in a non existing path
        r = self.app.post(endpoint, data=dict(path=self._invalid_irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)

        # Create a directory w/o passing a path
        r = self.app.post(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(
            r.status_code, self._hcodes.HTTP_BAD_METHOD_NOT_ALLOWED)

    def test_02_PUT_upload_entity(self):
        """ Test file upload: PUT """

        logger.info('*** Testing PUT')
        # Upload entity in test folder
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.put(endpoint, data=dict(
                         file=(io.BytesIO(b"this is a test"),
                               self._test_filename)),
                         headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Overwrite entity in test folder
        r = self.app.put(endpoint, data=dict(
                         file=(io.BytesIO(b"this is a test"),
                               self._test_filename), force='True'),
                         headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Overwrite entity in test folder w/o force flag
        r = self.app.put(endpoint, data=dict(
                         file=(io.BytesIO(b"this is a test"),
                               self._test_filename)),
                         headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)

        # Upload entity w/o passing a file
        r = self.app.put(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(
            r.status_code, self._hcodes.HTTP_BAD_METHOD_NOT_ALLOWED)

        # Upload entity in a non existing path
        endpoint = self._api_uri + \
            self._main_endpoint + self._invalid_irods_path
        r = self.app.put(endpoint, data=dict(
                         file=(io.BytesIO(b"this is a test"),
                               self._test_filename)),
                         headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)

    def test_03_GET_entities(self):
        """ Test the entity listingend retrieval: GET """

        logger.info('*** Testing GET')
        # GET non existing entity
        endpoint = (self._api_uri + self._main_endpoint +
                    self._irods_path + '/' + self._test_filename)
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)

        ###################################################
        # I need to upload some data to test the DELETE..
        # Create a directory
        endpoint = self._api_uri + self._main_endpoint
        r = self.app.post(endpoint, data=dict(path=self._irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Upload entity in test folder
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.put(endpoint, data=dict(
                         file=(io.BytesIO(b"this is a test"),
                               self._test_filename)),
                         headers=self.__class__.auth_header)
        ###################################################

        # Obtain entity metadata
        endpoint = (self._api_uri + self._main_endpoint +
                    self._irods_path + '/' + self._test_filename)
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Get list of entities in a directory
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Download an entity
        endpoint = (self._api_uri + self._main_endpoint +
                    self._irods_path + '/' + self._test_filename)
        r = self.app.get(endpoint, data=dict(download='True'),
                         headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        self.assertEqual(r.data, b'this is a test')

    def test_04_PATCH_rename(self):
        """ Test directory creation: POST """

        logger.info('*** Testing PATCH')
        
        new_file_name = "filetest1"
        new_directory_name = "directorytest1"

        ###################################################
        # I need to upload some data to test the DELETE..
        # Create a directory
        endpoint = self._api_uri + self._main_endpoint
        r = self.app.post(endpoint, data=dict(path=self._irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Upload entity in test folder
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.put(endpoint, data=dict(
                         file=(io.BytesIO(b"this is a test"),
                               self._test_filename)),
                         headers=self.__class__.auth_header)
        ###################################################

        # Rename file
        params = json.dumps(dict(newname=new_file_name))
        endpoint = (self._api_uri + self._main_endpoint +
                    self._irods_path + '/' + self._test_filename)
        r = self.app.patch(endpoint, data=params,
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Rename again with the original name
        params = json.dumps(dict(newname=self._test_filename))
        endpoint = (self._api_uri + self._main_endpoint +
                    self._irods_path + '/' + new_file_name)
        r = self.app.patch(endpoint, data=params,
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Rename directory
        params = json.dumps(dict(newname=new_directory_name))
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.patch(endpoint, data=params,
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Rename again with the original name
        params = json.dumps(dict(newname=self._irods_path))
        endpoint = self._api_uri + self._main_endpoint + new_directory_name
        r = self.app.patch(endpoint, data=params,
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Rename non existing file
        params = json.dumps(dict(newname=self._test_filename))
        endpoint = (self._api_uri + self._main_endpoint +
                    self._irods_path + '/' + new_file_name)
        r = self.app.patch(endpoint, data=params,
            headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)

        # Rename non existing directory
        params = json.dumps(dict(newname=self._irods_path))
        endpoint = self._api_uri + self._main_endpoint + new_directory_name
        r = self.app.patch(endpoint, data=params,
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Rename w/o passing "newname"
        endpoint = (self._api_uri + self._main_endpoint +
                    self._irods_path + '/' + new_file_name)
        r = self.app.patch(endpoint, data=dict(
            headers=self.__class__.auth_header))
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)

    def test_05_DELETE_entities(self):
        """ Test the entity delete: DELETE """

        ###################################################
        # I need to upload some data to test the DELETE..
        # Create a directory
        endpoint = self._api_uri + self._main_endpoint
        r = self.app.post(endpoint, data=dict(path=self._irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Upload entity in test folder
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.put(endpoint, data=dict(
                         file=(io.BytesIO(b"this is a test"),
                               self._test_filename)),
                         headers=self.__class__.auth_header)
        ###################################################

        logger.info('*** Testing DELETE')
        # Delete non empty directory
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)

        # Delete entity
        endpoint = (self._api_uri + self._main_endpoint + self._irods_path +
                    '/' + self._test_filename)
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Delete directory
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Delete non existing entity
        endpoint = (self._api_uri + self._main_endpoint + self._irods_path +
                    '/' + self._test_filename + 'x')
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)
        # HTTP_BAD_NOTFOUND is more appropriate

        # Delete non existing directory
        endpoint = self._api_uri \
            + self._main_endpoint + self._invalid_irods_path
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)

        # Delete w/o passing a path
        endpoint = self._api_uri + self._main_endpoint
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)

