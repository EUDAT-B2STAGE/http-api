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

    def test_01_whatever(self):
        """
        # TODO: SOMETHING

iadmin mkuser paolo rodsuser
iadmin moduser paolo password tester

http POST localhost:8080/auth/b2safeproxy username=paolo password=tester
or
nose2 -F tests.custom.test_b2safeproxy
        """

        endpoint = (self._auth_uri + self._main_endpoint)
        log.info('*** Testing auth b2safe on %s' % endpoint)
        r = self.app.post(
            endpoint,
            data=dict(username='paolo', password='tester')
        )

        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        data = json.loads(r.get_data(as_text=True))
        # log.pp(data)
        self.assertEqual(data['Response']['data'], 'Hello world!')

    # def tearDown(self):
    #     """ override original teardown if you create custom data """

    #     log.debug('### Cleaning custom data ###\n')
    #     super().tearDown()
