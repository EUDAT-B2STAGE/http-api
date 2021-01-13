import io

from restapi.tests import API_URI
from restapi.utilities.logs import log
from tests.custom import RestTestsAuthenticatedBase

IRODS_BASEPATH = "/tempZone/home/icatbetatester"
TEST_FILENAME = "test.txt"


class TestDigitalObjects(RestTestsAuthenticatedBase):
    def test_01_POST_create_test_directory(self):
        """ Test directory creation: POST """

        IRODS_PATH = f"{IRODS_BASEPATH}/testregistered1"
        log.info("*** Testing POST")

        # Create a directory
        endpoint = f"{API_URI}/registered"
        r = self.client.post(
            endpoint, data={"path": IRODS_PATH}, headers=self.__class__.auth_header,
        )
        assert r.status_code == 200

        # Overwrite a directory w/o force flag
        r = self.client.post(
            endpoint, data={"path": IRODS_PATH}, headers=self.__class__.auth_header,
        )
        assert r.status_code == 409

        # Overwrite a directory
        params = {"force": True, "path": IRODS_PATH}
        r = self.client.post(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Create a directory in a non existing path
        r = self.client.post(
            endpoint,
            data={"path": "/tempZone/home/x/icatbetatester/test"},
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 404

        # Create a directory w/o passing a path
        r = self.client.post(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 400

    def test_02_PUT_upload_entity(self):
        """ Test file upload: PUT """

        IRODS_PATH = f"{IRODS_BASEPATH}/testregistered2"
        ###################################################
        # Create a directory
        endpoint = f"{API_URI}/registered"
        r = self.client.post(
            endpoint, data={"path": IRODS_PATH}, headers=self.__class__.auth_header,
        )
        assert r.status_code == 200
        ###################################################

        log.info("*** Testing PUT")
        content = b"a test"
        # Upload entity in test folder
        endpoint = f"{API_URI}/registered{IRODS_PATH}/{TEST_FILENAME}"
        r = self.client.put(
            endpoint,
            data={"force": True, "file": (io.BytesIO(content), TEST_FILENAME)},
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200
        # Then verify content!
        r = self.client.get(
            endpoint,
            query_string={"download": True},
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200
        assert r.data == content

        log.info("*** Testing PUT in streaming")
        # Upload entity in test folder
        endpoint = f"{API_URI}/registered{IRODS_PATH}{TEST_FILENAME}2"
        content = b"verywell\nbla bla\n"
        r = self.client.put(
            endpoint,
            data=io.BytesIO(content),
            content_type="application/octet-stream",
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200
        # Then verify content!
        r = self.client.get(
            endpoint,
            query_string={"download": True},
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200
        assert r.data == content

        # Overwrite entity in test folder
        r = self.client.put(
            endpoint,
            data={
                "force": True,
                "file": (io.BytesIO(b"this is a test"), TEST_FILENAME),
            },
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200

        # Overwrite entity in test folder w/o force flag
        r = self.client.put(
            endpoint,
            data={"file": (io.BytesIO(b"this is a test"), TEST_FILENAME)},
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 400

        # Upload entity w/o passing a file
        r = self.client.put(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 400

        # Upload entity in a non existing path
        endpoint = f"{API_URI}/registered/tempZone/home/x/icatbetatester/test"
        r = self.client.put(
            endpoint,
            data={"file": (io.BytesIO(b"this is a test"), TEST_FILENAME)},
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 404

    def get_pid(self, response):

        # data = json.loads(r.get_data(as_text=True))
        data = self.get_content(response)

        # get the only file in the response
        data_object = data.pop().get(TEST_FILENAME, {})
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

        IRODS_PATH = f"{IRODS_BASEPATH}/testregistered3"
        pid = "123/123456789"
        # STRANGE_BSTRING = b"normal"
        STRANGE_BSTRING = "£$%&($)/(*é:_§°:#".encode()

        log.info("*** Testing GET")
        # GET non existing entity
        endpoint = f"{API_URI}/registered{IRODS_PATH}/{TEST_FILENAME}NOTEXISTS"
        r = self.client.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 404

        ###################################################
        # I need to upload some data..
        # Create a directory
        endpoint = f"{API_URI}/registered"
        r = self.client.post(
            endpoint, data={"path": IRODS_PATH}, headers=self.__class__.auth_header,
        )
        assert r.status_code == 200

        # Upload entity in test folder
        endpoint = f"{API_URI}/registered" + IRODS_PATH
        r = self.client.put(
            endpoint,
            data={"file": (io.BytesIO(STRANGE_BSTRING), TEST_FILENAME)},
            headers=self.__class__.auth_header,
        )
        # ###################################################

        # Get list of entities in a directory
        endpoint = f"{API_URI}/registered" + IRODS_PATH
        r = self.client.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Obtain entity metadata
        endpoint = f"{API_URI}/registered" + IRODS_PATH + "/" + TEST_FILENAME
        r = self.client.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Download an entity
        endpoint = f"{API_URI}/registered" + IRODS_PATH + "/" + TEST_FILENAME
        r = self.client.get(
            endpoint,
            query_string={"download": True},
            headers=self.__class__.auth_header,
        )
        assert r.status_code == 200
        assert r.data == STRANGE_BSTRING

        # Obtain EUDAT entity metadata (not present)
        endpoint = f"{API_URI}/registered" + IRODS_PATH + "/" + TEST_FILENAME
        r = self.client.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 200

        response_pid = self.get_pid(r)
        assert response_pid is None

        # Add EUDAT metadata
        params = {"PID": pid}
        endpoint = API_URI + "/metadata" + IRODS_PATH + "/" + TEST_FILENAME
        r = self.client.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Obtain EUDAT entity metadata
        endpoint = f"{API_URI}/registered" + IRODS_PATH + "/" + TEST_FILENAME
        r = self.client.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 200

        response_pid = self.get_pid(r)
        assert response_pid == pid

    def test_04_PATCH_rename(self):
        """ Test directory creation: POST """

        log.info("*** Testing PATCH")

        IRODS_PATH = f"{IRODS_BASEPATH}/testregistered4"
        new_file_name = "filetest1"
        new_directory_name = "directorytest1"

        ###################################################
        # I need to upload some data to test the DELETE..
        # Create a directory
        endpoint = f"{API_URI}/registered"
        r = self.client.post(
            endpoint, data={"path": IRODS_PATH}, headers=self.__class__.auth_header,
        )
        assert r.status_code == 200

        # Upload entity in test folder
        endpoint = f"{API_URI}/registered" + IRODS_PATH
        r = self.client.put(
            endpoint,
            data={"file": (io.BytesIO(b"this is a test"), TEST_FILENAME)},
            headers=self.__class__.auth_header,
        )
        ###################################################

        # Rename file
        params = {"newname": new_file_name}
        endpoint = f"{API_URI}/registered" + IRODS_PATH + "/" + TEST_FILENAME
        r = self.client.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Rename again with the original name
        params = {"newname": TEST_FILENAME}
        endpoint = f"{API_URI}/registered" + IRODS_PATH + "/" + new_file_name
        r = self.client.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Rename directory
        params = {"newname": new_directory_name}
        endpoint = f"{API_URI}/registered" + IRODS_PATH
        r = self.client.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Rename again with the original name
        params = {"newname": "test"}
        irods_home = "/tempZone/home/icatbetatester"
        endpoint = f"{API_URI}/registered" + irods_home + "/" + new_directory_name
        r = self.client.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 200

        # Rename non existing file
        params = {"newname": TEST_FILENAME}
        endpoint = f"{API_URI}/registered" + IRODS_PATH + "/" + new_file_name
        r = self.client.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 404

        # Rename non existing directory
        params = {"newname": IRODS_PATH}
        endpoint = f"{API_URI}/registered" + new_directory_name
        r = self.client.patch(endpoint, data=params, headers=self.__class__.auth_header)
        assert r.status_code == 404

        # Rename w/o passing "newname"
        endpoint = f"{API_URI}/registered" + IRODS_PATH + "/" + new_file_name
        r = self.client.patch(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 400

    def test_05_DELETE_entities(self):
        """ Test the entity delete: DELETE """

        IRODS_PATH = f"{IRODS_BASEPATH}/testregistered5"
        ###################################################
        # I need to upload some data to test the DELETE..
        # Create a directory
        endpoint = f"{API_URI}/registered"
        r = self.client.post(
            endpoint, data={"path": IRODS_PATH}, headers=self.__class__.auth_header,
        )
        assert r.status_code == 200

        # Upload entity in test folder
        endpoint = f"{API_URI}/registered" + IRODS_PATH
        r = self.client.put(
            endpoint,
            data={"file": (io.BytesIO(b"this is a test"), TEST_FILENAME)},
            headers=self.__class__.auth_header,
        )
        ###################################################

        log.info("*** Testing DELETE")

        # Delete entity
        endpoint = f"{API_URI}/registered" + IRODS_PATH + "/" + TEST_FILENAME
        r = self.client.delete(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 405

        # Delete directory
        endpoint = f"{API_URI}/registered" + IRODS_PATH
        r = self.client.delete(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 405

        # Delete non existing entity
        endpoint = f"{API_URI}/registered" + IRODS_PATH + "/" + TEST_FILENAME + "x"
        r = self.client.delete(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 405
