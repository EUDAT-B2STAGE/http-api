# -*- coding: utf-8 -*-

"""
Run unittests inside the RAPyDo framework
"""

from tests.custom import RestTestsAuthenticatedBase
from restapi.utilities.logs import log


class TestB2safeProxy(RestTestsAuthenticatedBase):

    _main_endpoint = '/b2safeproxy'
    _irods_user = 'icatbetatester'
    _irods_password = 'IAMABETATESTER'

    def test_01_b2safe_login(self):

        endpoint = (self._auth_uri + self._main_endpoint)
        log.info('*** Testing auth b2safe on {}', endpoint)
        r = self.app.post(
            endpoint,
            data=dict(
                username=self._irods_user, password=self._irods_password
            )
        )

        assert r.status_code == 200
        data = self.get_content(r)
        assert 'token' in data
        token = data.get('token')
        self.save_token(token)

        # verify that token is valid
        r = self.app.get(
            endpoint, headers={'Authorization': 'Bearer {}'.format(token)})
        assert r.status_code == 200
        assert 'validated' == self.get_content(r)

        # verify wrong username or password
        r = self.app.post(
            endpoint, data=dict(
                username=self._irods_user + 'a',
                password=self._irods_password
            )
        )
        assert r.status_code == 401
        r = self.app.post(
            endpoint, data=dict(
                username=self._irods_user,
                password=self._irods_password + 'b'
            )
        )
        assert r.status_code == 401

        # verify random token
        wrong_token = token.lower().replace('e', 'Z').replace('j', 'i')
        r = self.app.get(
            endpoint, headers={'Authorization': 'Bearer {}'.format(wrong_token)})
        assert r.status_code == 401
