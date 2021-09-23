from typing import Any, Dict

from restapi.env import Env
from restapi.tests import AUTH_URI, BaseTests, FlaskClient

IRODS_USER = Env.get("IRODS_USER")
IRODS_PASSWORD = Env.get("IRODS_PASSWORD")


class SeadataTests(BaseTests):
    def login(self, client: FlaskClient) -> Dict[str, str]:

        r = client.post(
            f"{AUTH_URI}/b2safeproxy",
            data={"username": IRODS_USER, "password": IRODS_PASSWORD},
        )

        assert r.status_code == 200
        data = self.get_content(r)
        assert "Response" in data
        assert "data" in data["Response"]
        assert "token" in data["Response"]["data"]

        token = data["Response"]["data"]["token"]
        assert token is not None

        return {"Authorization": f"Bearer {token}"}

    def test_endpoints_input_schema(self, response: Dict[str, Any]) -> None:
        assert "api_function" in response
        assert "Missing data for required field." in response["api_function"]

        assert "datetime" in response
        assert "Missing data for required field." in response["datetime"]

        assert "edmo_code" in response
        assert "Missing data for required field." in response["edmo_code"]

        assert "parameters" in response
        assert "Missing data for required field." in response["parameters"]

        assert "request_id" in response
        assert "Missing data for required field." in response["request_id"]

        assert "test_mode" in response
        assert "Missing data for required field." in response["test_mode"]

        assert "version" in response
        assert "Missing data for required field." in response["version"]
