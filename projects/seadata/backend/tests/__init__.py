from typing import Dict

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
        assert "token" in data
        token = data.get("token")

        assert token is not None

        return {"Authorization": f"Bearer {token}"}
