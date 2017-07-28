# -*- coding: utf-8 -*-

"""
Run unittests inside the RAPyDo framework
"""

import json
from tests import RestTestsAuthenticatedBase
from utilities.logs import get_logger

log = get_logger(__name__)


class TestB2safeProxy(RestTestsAuthenticatedBase):

    _main_endpoint = '/b2safeproxy'
    _irods_user = 'icatbetatester'
    _irods_password = 'IAMABETATESTER'

    def setUp(self):
        super().setUp()
        log.warning("Paolo START")

        # iadmin mkuser paolo rodsuser
        # iadmin moduser paolo password tester

    def tearDown(self):
        # log.debug('### Cleaning custom data ###\n')
        log.warning("Paolo END")
        super().tearDown()

    def test_01_whatever(self):
        """
        To create a user and test it:
        nose2 -F tests.custom.test_b2safeproxy
        """

        endpoint = (self._auth_uri + self._main_endpoint)
        log.info('*** Testing auth b2safe on %s' % endpoint)
        r = self.app.post(
            endpoint,
            data=dict(username='paolo', password='tester')
        )

        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        json_output = json.loads(r.get_data(as_text=True))
        data = json_output.get('Response', {}).get('data', {})
        key = 'token'
        self.assertIn(key, data)
        token = data.get(key)
        print(token[0])

        # verify that token is valid

        # verify that normal token from normal login is invalid

        # verify wrong username or password

        # verify random token
