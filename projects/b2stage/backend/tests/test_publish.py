# -*- coding: utf-8 -*-

"""
Run unittests inside the RAPyDo framework
"""

import json
from tests import RestTestsAuthenticatedBase
from utilities.logs import get_logger

log = get_logger(__name__)


class TestPublish(RestTestsAuthenticatedBase):

    _auth_endpoint = '/b2safeproxy'
    _main_endpoint = '/publish'
    _anonymous_user = 'anonymous'

    def setUp(self):

        # Call father's method
        super().setUp()

        log.info("\n### Creating a test token (for ANONYMOUS IRODS user) ###")
        credentials = json.dumps({'username': self._anonymous_user})
        endpoint = self._auth_uri + self._auth_endpoint

        log.debug('*** Testing anonymous authentication on %s' % endpoint)
        r = self.app.post(endpoint, data=credentials)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        content = self.get_content(r)
        self.save_token(content.get('token'), suffix=self._anonymous_user)

    def test_01_GET_giveityourname(self):
        pass

    #     endpoint = (self._api_uri + self._main_endpoint)
    #     log.info('*** Testing GET call on %s' % endpoint)

    #     r = self.app.get(endpoint)  # If NO authorization required
    #     # r = self.app.get(
    #     #     endpoint,
    #     #     headers=self.__class__.auth_header  # If authorization required
    #     # )

    #     # Assert what is right or wrong
    #     self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
    #     data = json.loads(r.get_data(as_text=True))

    #     # pretty print data obtained from API to check the content
    #     # log.pp(data)
    #     self.assertEqual(data['Response']['data'], 'Hello world!')

    def tearDown(self):

        # Token clean up
        log.debug('\n### Cleaning anonymous data ###')
        ep = self._auth_uri + '/tokens'

        # Recover current token id
        r = self.app.get(ep, headers=self.__class__.auth_header_anonymous)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        content = self.get_content(r)
        for element in content:
            if element.get('token') == self.__class__.bearer_token_anonymous:
                # delete only current token
                ep += '/' + element.get('id')
                rdel = self.app.delete(ep, headers=self.__class__.auth_header_anonymous)
                self.assertEqual(
                    rdel.status_code, self._hcodes.HTTP_OK_NORESPONSE)

        # The end
        super().tearDown()
