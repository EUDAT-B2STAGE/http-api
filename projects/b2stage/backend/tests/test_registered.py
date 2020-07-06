import io
import json

from restapi.tests import API_URI
from restapi.utilities.logs import log
from tests.custom import RestTestsAuthenticatedBase


class TestDigitalObjects(RestTestsAuthenticatedBase):

    _irods_test_name = "test"
    _irods_home = "/tempZone/home/icatbetatester"
    _irods_path = "/tempZone/home/icatbetatester/test"
    _invalid_irods_path = "/tempZone/home/x/icatbetatester/test"
    _test_pdf_filename = "test.pdf"
    _test_filename = "test.txt"

    def tearDown(self):

        log.debug("### Cleaning custom data ###\n")

        # Clean all test data
        endpoint = f"{API_URI}/registered"
        r = self.app.delete(
            endpoint, data=dict(debugclean="True"), headers=self.__class__.auth_header
        )
        assert r.status_code == 200

        super().tearDown()

    def test_01_POST_create_test_directory(self):
        """ Test directory creation: POST """

        log.info("*** Testing POST")

        # Create a directory
        endpoint = f"{API_URI}/registered"
        r = self.app.post(
            endpoint,
            data=dict(path=self._irods_path),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200

        # Overwrite a directory w/o force flag
        r = self.app.post(
            endpoint,
            data=dict(path=self._irods_path),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 409

        # Overwrite a directory
        params = json.dumps(dict(force=True, path=self._irods_path))
        r = self.app.post(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Create a directory in a non existing path
        r = self.app.post(
            endpoint,
            data=dict(path=self._invalid_irods_path),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 404

        # Create a directory w/o passing a path
        r = self.app.post(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 405

    def test_02_PUT_upload_entity(self):
        """ Test file upload: PUT """

        ###################################################
        # Create a directory
        endpoint = f"{API_URI}/registered"
        r = self.app.post(
            endpoint,
            data=dict(path=self._irods_path),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200
        ###################################################

        log.info("*** Testing PUT")
        content = b"a test"
        # Upload entity in test folder
        endpoint = f"{API_URI}/registered{self._irods_path}/{self._test_filename}"
        r = self.app.put(
            endpoint,
            data=dict(force=True, file=(io.BytesIO(content), self._test_filename)),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200
        # Then verify content!
        r = self.app.get(
            endpoint, data=dict(download="True"), headers=self.__class__.auth_header
        )
        assert r.status_code == 200
        assert r.data == content

        log.info("*** Testing PUT in streaming")
        # Upload entity in test folder
        endpoint = f"{API_URI}/registered{self._irods_path}{self._test_filename}2"
        content = b"verywell\nbla bla\n"
        r = self.app.put(
            endpoint,
            data=io.BytesIO(content),
            content_type="application/octet-stream",
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200
        # Then verify content!
        r = self.app.get(
            endpoint, data=dict(download="True"), headers=self.__class__.auth_header
        )
        assert r.status_code == 200
        assert r.data == content

        # Overwrite entity in test folder
        r = self.app.put(
            endpoint,
            data=dict(
                file=(io.BytesIO(b"this is a test"), self._test_filename), force="True"
            ),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200

        # Overwrite entity in test folder w/o force flag
        r = self.app.put(
            endpoint,
            data=dict(file=(io.BytesIO(b"this is a test"), self._test_filename)),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 400

        # Upload entity w/o passing a file
        r = self.app.put(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 400

        # Upload entity in a non existing path
        endpoint = f"{API_URI}/registered{self._invalid_irods_path}"
        r = self.app.put(
            endpoint,
            data=dict(file=(io.BytesIO(b"this is a test"), self._test_filename)),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 404

    def get_pid(self, response):

        # data = json.loads(r.get_data(as_text=True))
        data = self.get_content(response)

        # get the only file in the response
        data_object = data.pop().get(self._test_filename, {})
        # check for metadata
        key = "metadata"
        assert key in data_object
        metadata = data_object.get(key)
        # check for PID
        key = "PID"
        assert key in metadata
        return metadata.get(key)

    def test_03_GET_entities(self):
        """ Test the entity listingend retrieval: GET """

        pid = "123/123456789"
        # STRANGE_BSTRING = b"normal"
        STRANGE_BSTRING = "£$%&($)/(*é:_§°:#".encode()

        log.info("*** Testing GET")
        # GET non existing entity
        endpoint = (
            f"{API_URI}/registered{self._irods_path}/{self._test_filename}NOTEXISTS"
        )
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 404

        ###################################################
        # I need to upload some data..
        # Create a directory
        endpoint = f"{API_URI}/registered"
        r = self.app.post(
            endpoint,
            data=dict(path=self._irods_path),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200

        # Upload entity in test folder
        endpoint = f"{API_URI}/registered" + self._irods_path
        r = self.app.put(
            endpoint,
            data=dict(file=(io.BytesIO(STRANGE_BSTRING), self._test_filename)),
            headers=self.__class__.auth_header,
        )
        # ###################################################

        # Get list of entities in a directory
        endpoint = f"{API_URI}/registered" + self._irods_path
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Obtain entity metadata
        endpoint = (
            f"{API_URI}/registered" + self._irods_path + "/" + self._test_filename
        )
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Download an entity
        endpoint = (
            f"{API_URI}/registered" + self._irods_path + "/" + self._test_filename
        )
        r = self.app.get(
            endpoint, data=dict(download="True"), headers=self.__class__.auth_header
        )
        assert r.status_code == 200
        assert r.data == STRANGE_BSTRING

        # Obtain EUDAT entity metadata (not present)
        endpoint = (
            f"{API_URI}/registered" + self._irods_path + "/" + self._test_filename
        )
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 200

        response_pid = self.get_pid(r)
        assert response_pid is None

        # Add EUDAT metadata
        params = json.dumps(dict({"PID": pid}))
        endpoint = API_URI + "/metadata" + self._irods_path + "/" + self._test_filename
        r = self.app.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Obtain EUDAT entity metadata
        endpoint = (
            f"{API_URI}/registered" + self._irods_path + "/" + self._test_filename
        )
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 200

        response_pid = self.get_pid(r)
        assert response_pid == pid

    def test_04_PATCH_rename(self):
        """ Test directory creation: POST """

        log.info("*** Testing PATCH")

        new_file_name = "filetest1"
        new_directory_name = "directorytest1"

        ###################################################
        # I need to upload some data to test the DELETE..
        # Create a directory
        endpoint = f"{API_URI}/registered"
        r = self.app.post(
            endpoint,
            data=dict(path=self._irods_path),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200

        # Upload entity in test folder
        endpoint = f"{API_URI}/registered" + self._irods_path
        r = self.app.put(
            endpoint,
            data=dict(file=(io.BytesIO(b"this is a test"), self._test_filename)),
            headers=self.__class__.auth_header,
        )
        ###################################################

        # Rename file
        params = json.dumps(dict(newname=new_file_name))
        endpoint = (
            f"{API_URI}/registered" + self._irods_path + "/" + self._test_filename
        )
        r = self.app.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Rename again with the original name
        params = json.dumps(dict(newname=self._test_filename))
        endpoint = f"{API_URI}/registered" + self._irods_path + "/" + new_file_name
        r = self.app.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Rename directory
        params = json.dumps(dict(newname=new_directory_name))
        endpoint = f"{API_URI}/registered" + self._irods_path
        r = self.app.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Rename again with the original name
        params = json.dumps(dict(newname=self._irods_test_name))
        endpoint = f"{API_URI}/registered" + self._irods_home + "/" + new_directory_name
        r = self.app.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Rename non existing file
        params = json.dumps(dict(newname=self._test_filename))
        endpoint = f"{API_URI}/registered" + self._irods_path + "/" + new_file_name
        r = self.app.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 404

        # Rename non existing directory
        params = json.dumps(dict(newname=self._irods_path))
        endpoint = f"{API_URI}/registered" + new_directory_name
        r = self.app.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 404

        # Rename w/o passing "newname"
        endpoint = f"{API_URI}/registered" + self._irods_path + "/" + new_file_name
        r = self.app.patch(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 400

    def test_05_DELETE_entities(self):
        """ Test the entity delete: DELETE """

        ###################################################
        # I need to upload some data to test the DELETE..
        # Create a directory
        endpoint = f"{API_URI}/registered"
        r = self.app.post(
            endpoint,
            data=dict(path=self._irods_path),
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200

        # Upload entity in test folder
        endpoint = f"{API_URI}/registered" + self._irods_path
        r = self.app.put(
            endpoint,
            data=dict(file=(io.BytesIO(b"this is a test"), self._test_filename)),
            headers=self.__class__.auth_header,
        )
        ###################################################

        log.info("*** Testing DELETE")

        # Delete entity
        endpoint = (
            f"{API_URI}/registered" + self._irods_path + "/" + self._test_filename
        )
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 405

        # Delete directory
        endpoint = f"{API_URI}/registered" + self._irods_path
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 405

        # Delete non existing entity
        endpoint = (
            f"{API_URI}/registered" + self._irods_path + "/" + self._test_filename + "x"
        )
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 405
