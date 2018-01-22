# -*- coding: utf-8 -*-

from tests import RestTestsAuthenticatedBase
from utilities.logs import get_logger

log = get_logger(__name__)


class TestResources(RestTestsAuthenticatedBase):

    _main_endpoint = '/internals/resources'

    def test_01_GET_sometest(self):

        assert True

        # endpoint = (self._api_uri + self._main_endpoint)
        # log.info('*** Testing GET call on %s' % endpoint)

        # r = self.app.get(endpoint)  # If NO authorization required
        # # r = self.app.get(
        # #     endpoint,
        # #     headers=self.__class__.auth_header  # If authorization required
        # # )

        # # Assert what is right or wrong
        # self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        # output = self.get_content(r)

        # # pretty print data obtained from API to check the content
        # # log.pp(output)
        # self.assertEqual(output, 'Hello world!')
