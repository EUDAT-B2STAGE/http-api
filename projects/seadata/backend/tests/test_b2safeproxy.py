# -*- coding: utf-8 -*-

"""
Run unittests inside the RAPyDo framework
"""

from tests import RestTestsAuthenticatedBase
from utilities.logs import get_logger

log = get_logger(__name__)


class TestB2safeProxy(RestTestsAuthenticatedBase):

    _main_endpoint = '/b2safeproxy'
    _irods_service = 'irods'
    _irods_user = 'icatbetatester'
    _irods_password = 'IAMABETATESTER'

    def setUp(self):
        """
        add a user for irods to be tested with direct credentials
        """

        super().setUp()
        log.debug('### Creating custom data ###\n')
        # how to get a service before having any app request
        i = self.get_service_handler(self._irods_service)
        # create a dedicated irods user and set the password
        if i.create_user(self._irods_user):
            i.modify_user_password(self._irods_user, self._irods_password)

    def tearDown(self):
        """
        remove irods user created only for testing
        """

        log.debug('### Cleaning custom data ###\n')
        i = self.get_service_handler(self._irods_service)
        i.remove_user(self._irods_user)
        super().tearDown()

    def test_01_b2safe_login(self):

        endpoint = (self._auth_uri + self._main_endpoint)
        log.info('*** Testing auth b2safe on %s' % endpoint)
        r = self.app.post(
            endpoint,
            data=dict(
                username=self._irods_user, password=self._irods_password
            )
        )

        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        data = self.get_content(r)
        key = 'token'
        self.assertIn(key, data)
        token = data.get(key)

        # verify that token is valid
        r = self.app.get(
            endpoint, headers={'Authorization': 'Bearer %s' % token})
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        self.assertEqual('validated', self.get_content(r))

        # verify wrong username or password
        r = self.app.post(
            endpoint, data=dict(
                username=self._irods_user + 'a',
                password=self._irods_password
            )
        )
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_UNAUTHORIZED)
        r = self.app.post(
            endpoint, data=dict(
                username=self._irods_user,
                password=self._irods_password + 'b'
            )
        )
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_UNAUTHORIZED)

        # verify random token
        wrong_token = token.lower().replace('e', 'Z').replace('j', 'i')
        r = self.app.get(
            endpoint, headers={'Authorization': 'Bearer %s' % wrong_token})
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_UNAUTHORIZED)

        # verify that normal token from normal login is invalid
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_UNAUTHORIZED)
