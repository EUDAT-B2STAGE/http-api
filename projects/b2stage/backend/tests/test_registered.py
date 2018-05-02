# -*- coding: utf-8 -*-

"""
Test dataobjects endpoints

Run single test:
nose2 test.custom.test_dataobjects.TestDataObjects.test_07_delete_dataobjects
"""

import io
import json
from tests import RestTestsAuthenticatedBase
from utilities.logs import get_logger

__authors__ = [
    'Roberto Mucci (r.mucci@cineca.it)',
    "Paolo D'Onorio De Meo <p.donoriodemeo@cineca.it>",
]

log = get_logger(__name__)


class TestDigitalObjects(RestTestsAuthenticatedBase):

    _main_endpoint = '/registered'
    _metadata_endpoint = '/metadata'
    _irods_test_name = 'test'
    _irods_home = '/tempZone/home/guest'
    _irods_path = '/tempZone/home/guest/test'
    _invalid_irods_path = '/tempZone/home/x/guest/test'
    _test_pdf_filename = 'test.pdf'
    _test_filename = 'test.txt'

    def tearDown(self):

        log.debug('### Cleaning custom data ###\n')

        # Clean all test data
        endpoint = self._api_uri + self._main_endpoint
        r = self.app.delete(endpoint, data=dict(debugclean='True'),
                            headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        super().tearDown()

    def test_01_POST_create_test_directory(self):
        """ Test directory creation: POST """

        log.info('*** Testing POST')

        # Create a directory
        endpoint = self._api_uri + self._main_endpoint
        r = self.app.post(endpoint, data=dict(path=self._irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Overwrite a directory w/o force flag
        r = self.app.post(endpoint, data=dict(path=self._irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)

        # Overwrite a directory
        params = json.dumps(dict(force=True, path=self._irods_path))
        r = self.app.post(endpoint, data=params,
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Create a directory in a non existing path
        r = self.app.post(endpoint, data=dict(path=self._invalid_irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)

        # Create a directory w/o passing a path
        r = self.app.post(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(
            r.status_code, self._hcodes.HTTP_BAD_METHOD_NOT_ALLOWED)

    def test_02_PUT_upload_entity(self):
        """ Test file upload: PUT """

        ###################################################
        # Create a directory
        endpoint = self._api_uri + self._main_endpoint
        r = self.app.post(endpoint, data=dict(path=self._irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        ###################################################

        log.info('*** Testing PUT')
        content = b"a test"
        # Upload entity in test folder
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.put(endpoint, data=dict(
                         file=(io.BytesIO(content), self._test_filename)),
                         headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        # Then verify content!
        endpoint += '/' + self._test_filename
        r = self.app.get(
            endpoint, data=dict(download='True'),
            headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        self.assertEqual(r.data, content)

        log.info('*** Testing PUT in streaming')
        # Upload entity in test folder
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_path + self._test_filename + '2'
        content = b"verywell\nbla bla\n"
        r = self.app.put(
            endpoint, data=io.BytesIO(content),
            content_type='application/octet-stream',
            headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        # Then verify content!
        r = self.app.get(
            endpoint, data=dict(download='True'),
            headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        self.assertEqual(r.data, content)

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
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)

    def get_pid(self, response):

        # data = json.loads(r.get_data(as_text=True))
        data = self.get_content(response)

        # get the only file in the response
        data_object = data.pop().get(self._test_filename, {})
        # check for metadata
        key = 'metadata'
        self.assertIn(key, data_object)
        metadata = data_object.get(key)
        # check for PID
        key = 'PID'
        self.assertIn(key, metadata)
        return metadata.get(key)

    def test_03_GET_entities(self):
        """ Test the entity listingend retrieval: GET """

        pid = '123/123456789'
        # STRANGE_BSTRING = b"normal"
        STRANGE_BSTRING = "£$%&($)/(*é:_§°:#".encode()

        log.info('*** Testing GET')
        # GET non existing entity
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_path + '/' + self._test_filename + 'NOTEXISTS'
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)

        ###################################################
        # I need to upload some data..
        # Create a directory
        endpoint = self._api_uri + self._main_endpoint
        r = self.app.post(endpoint, data=dict(path=self._irods_path),
                          headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Upload entity in test folder
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.put(endpoint, data=dict(
                         file=(io.BytesIO(STRANGE_BSTRING),
                               self._test_filename)),
                         headers=self.__class__.auth_header)
        # ###################################################

        # Get list of entities in a directory
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Obtain entity metadata
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_path + '/' + self._test_filename
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Download an entity
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_path + '/' + self._test_filename
        r = self.app.get(endpoint, data=dict(download='True'),
                         headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        self.assertEqual(r.data, STRANGE_BSTRING)

        # Obtain EUDAT entity metadata (not present)
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_path + '/' + self._test_filename
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        response_pid = self.get_pid(r)
        self.assertEqual(response_pid, None)

        # Add EUDAT metadata
        params = json.dumps(dict({'PID': pid}))
        endpoint = self._api_uri + self._metadata_endpoint + \
            self._irods_path + '/' + self._test_filename
        r = self.app.patch(endpoint, data=params,
                           headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Obtain EUDAT entity metadata
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_path + '/' + self._test_filename
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        response_pid = self.get_pid(r)
        self.assertEqual(response_pid, pid)

        # Uncomment when iRODS forces checksum calculation
        # self.assertIsNotNone(
        #    data['Response']['data'][0][self._test_filename]['metadata']['checksum'])

    def test_04_PATCH_rename(self):
        """ Test directory creation: POST """

        log.info('*** Testing PATCH')

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
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_path + '/' + self._test_filename
        r = self.app.patch(endpoint, data=params,
                           headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Rename again with the original name
        params = json.dumps(dict(newname=self._test_filename))
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_path + '/' + new_file_name
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
        params = json.dumps(dict(newname=self._irods_test_name))
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_home + '/' + new_directory_name
        r = self.app.patch(endpoint, data=params,
                           headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Rename non existing file
        params = json.dumps(dict(newname=self._test_filename))
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_path + '/' + new_file_name
        r = self.app.patch(endpoint, data=params,
                           headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)

        # Rename non existing directory
        params = json.dumps(dict(newname=self._irods_path))
        endpoint = self._api_uri + self._main_endpoint + new_directory_name
        r = self.app.patch(endpoint, data=params,
                           headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)

        # Rename w/o passing "newname"
        endpoint = self._api_uri + self._main_endpoint + \
            self._irods_path + '/' + new_file_name
        r = self.app.patch(endpoint, headers=self.__class__.auth_header)
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

        log.info('*** Testing DELETE')

        # # Delete non empty directory
        # endpoint = self._api_uri + self._main_endpoint + self._irods_path
        # r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        # self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)

        # Delete entity
        endpoint = self._api_uri + self._main_endpoint + self._irods_path + \
            '/' + self._test_filename
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        # self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        self.assertEqual(
            r.status_code, self._hcodes.HTTP_BAD_METHOD_NOT_ALLOWED)

        # Delete directory
        endpoint = self._api_uri + self._main_endpoint + self._irods_path
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        # self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        self.assertEqual(
            r.status_code, self._hcodes.HTTP_BAD_METHOD_NOT_ALLOWED)

        # Delete non existing entity
        endpoint = self._api_uri + self._main_endpoint + self._irods_path + \
            '/' + self._test_filename + 'x'
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        # self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)
        self.assertEqual(
            r.status_code, self._hcodes.HTTP_BAD_METHOD_NOT_ALLOWED)

        # # Delete non existing directory
        # endpoint = self._api_uri \
        #     + self._main_endpoint + self._invalid_irods_path
        # r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        # self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)

        # # Delete w/o passing a path
        # endpoint = self._api_uri + self._main_endpoint
        # r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        # self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_REQUEST)
