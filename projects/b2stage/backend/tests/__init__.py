import json
import unittest

from b2stage.connectors import irods
from restapi.server import create_app
from restapi.tests import AUTH_URI
from restapi.utilities.logs import log

IRODS_USER = "icatbetatester"
IRODS_PASSWORD = "IAMABETATESTER"


class RestTestsAuthenticatedBase(unittest.TestCase):
    def setUp(self):

        self.client = create_app().test_client()

        log.debug("### Setting up the Flask server ###")

        i = irods.get_instance()
        # create a dedicated irods user and set the password
        if i.create_user(IRODS_USER):
            i.modify_user_password(IRODS_USER, IRODS_PASSWORD)

        r = self.client.post(
            AUTH_URI + "/b2safeproxy",
            data={"username": IRODS_USER, "password": IRODS_PASSWORD},
        )

        assert r.status_code == 200
        data = self.get_content(r)
        assert "token" in data
        token = data.get("token")
        self.save_token(token)

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
