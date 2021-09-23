import json
from datetime import datetime
from typing import Any, Dict, List, Union, cast

from flask.wrappers import Response
from restapi.env import Env
from restapi.tests import AUTH_URI, BaseTests, FlaskClient

IRODS_USER = Env.get("IRODS_USER")
IRODS_PASSWORD = Env.get("IRODS_PASSWORD")


class SeadataTests(BaseTests):
    def get_seadata_response(
        self, http_out: Response
    ) -> Union[str, float, int, bool, List[Any], Dict[str, Any]]:

        response = self.get_content(http_out)
        assert "Response" in response
        assert "data" in response["Response"]

        return cast(
            Union[str, float, int, bool, List[Any], Dict[str, Any]],
            response["Response"]["data"],
        )

    def login(self, client: FlaskClient) -> Dict[str, str]:

        r = client.post(
            f"{AUTH_URI}/b2safeproxy",
            data={"username": IRODS_USER, "password": IRODS_PASSWORD},
        )

        assert r.status_code == 200
        data = self.get_seadata_response(r)
        assert "token" in data

        token = data["token"]
        assert token is not None

        return {"Authorization": f"Bearer {token}"}

    def check_endpoints_input_schema(self, response: Dict[str, Any]) -> None:
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

    def get_input_data(self) -> Dict[str, Union[bool, int, str]]:
        data = {
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%s"),
            "edmo_code": 1234,
            "parameters": json.dumps({}),
            "request_id": "my_request_id",
            "test_mode": "1",
            "version": "1",
            "eudat_backdoor": True,
        }
        return data
