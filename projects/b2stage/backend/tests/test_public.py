# -*- coding: utf-8 -*-

""" To be defined from designing this endoint """

from tests import RestTestsAuthenticatedBase
from utilities.logs import get_logger

log = get_logger(__name__)


class TestPublic(RestTestsAuthenticatedBase):

    _main_endpoint = '/public'

    # def setUp(self):
    #     """ override original setup to create custom data at each request """

    #     super().setUp()  # Call father's method
    #     log.debug('### Create some custom data ###\n')

    def test_01_GET_public_data(self):

        # not official at the moment
        assert True

        # endpoint = (self._api_uri + self._main_endpoint)
        # log.info('*** Testing GET call on %s' % endpoint)

        # r = self.app.get(endpoint)
        # self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        # output = self.get_content(r)
        # # log.pp(output)
        # self.assertEqual(output, 'Hello world!')

    # def tearDown(self):
    #     """ override teardown: remove custom data at each request """

    #     log.debug('### Cleaning custom data ###\n')
    #     super().tearDown()
