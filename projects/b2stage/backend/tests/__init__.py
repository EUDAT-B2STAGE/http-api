import json
import unittest

from b2stage.connectors import irods
from restapi.server import create_app
from restapi.tests import AUTH_URI
from restapi.utilities.logs import log

IRODS_USER = "icatbetatester"
IRODS_PASSWORD = "IAMABETATESTER"


class RestTestsAuthenticatedBase(unittest.TestCase):

    """
    HOW TO

    # initialization logic for the test suite declared in the test module
    # code that is executed before all tests in one test run
    @classmethod
    def setUpClass(cls):
        pass

    # clean up logic for the test suite declared in the test module
    # code that is executed after all tests in one test run
    @classmethod
    def tearDownClass(cls):
        pass

    # initialization logic
    # code that is executed before each test
    def setUp(self):
        pass

    # clean up logic
    # code that is executed after each test
    def tearDown(self):
        pass
    """

    def setUp(self):

        client = create_app().test_client()

        log.debug("### Setting up the Flask server ###")

        i = irods.get_instance()
        # create a dedicated irods user and set the password
        if i.create_user(IRODS_USER):
            i.modify_user_password(IRODS_USER, IRODS_PASSWORD)

        r = client.post(
            AUTH_URI + "/b2safeproxy",
            data={"username": IRODS_USER, "password": IRODS_PASSWORD},
        )

        assert r.status_code == 200
        data = self.get_content(r)
        assert "token" in data
        token = data.get("token")
        self.save_token(token)

    def tearDown(self, client):

        # Token clean up
        log.debug("### Cleaning token ###")
        ep = f"{AUTH_URI}/tokens"
        # Recover current token id
        r = client.get(ep, headers=self.__class__.auth_header)
        assert r.status_code == 200
        content = self.get_content(r)
        for element in content:
            if element.get("token") == self.__class__.bearer_token:
                # delete only current token
                ep += "/" + element.get("id")
                rdel = client.delete(ep, headers=self.__class__.auth_header)
                assert rdel.status_code == 204

        # The end
        log.debug("### Tearing down the Flask server ###")

    def save_token(self, token, suffix=None):

        if suffix is None:
            suffix = ""
        else:
            suffix = "_" + suffix

        key = "bearer_token" + suffix
        setattr(self.__class__, key, token)

        key = "auth_header" + suffix
        setattr(self.__class__, key, {"Authorization": f"Bearer {token}"})

    def get_content(self, http_out):

        response = None

        try:
            response = json.loads(http_out.get_data().decode())
        except Exception as e:
            log.error("Failed to load response:\n{}", e)
            raise ValueError(f"Malformed response: {http_out}")

        return response
