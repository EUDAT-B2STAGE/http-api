"""
Run unittests inside the RAPyDo framework
"""

from restapi.tests import AUTH_URI
from restapi.utilities.logs import log
from tests.custom import RestTestsAuthenticatedBase


class TestB2safeProxy(RestTestsAuthenticatedBase):
    def test_01_b2safe_login(self):

        endpoint = f"{AUTH_URI}/b2safeproxy"
        log.info("*** Testing auth b2safe on {}", endpoint)
        r = self.app.post(
            endpoint,
            data=dict(username=self._irods_user, password=self._irods_password),
        )

        assert r.status_code == 200
        data = self.get_content(r)
        assert "token" in data
        token = data.get("token")
        self.save_token(token)

        # verify that token is valid
        r = self.app.get(endpoint, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert "validated" == self.get_content(r)

        # verify wrong username or password
        r = self.app.post(
            endpoint,
            data=dict(username=self._irods_user + "a", password=self._irods_password),
        )
        assert r.status_code == 401
        r = self.app.post(
            endpoint,
            data=dict(username=self._irods_user, password=self._irods_password + "b"),
        )
        assert r.status_code == 401

        # verify random token
        wrong_token = token.lower().replace("e", "Z").replace("j", "i")
        r = self.app.get(endpoint, headers={"Authorization": f"Bearer {wrong_token}"})
        assert r.status_code == 401
