# -*- coding: utf-8 -*-

from restapi.tests import BaseTests, API_URI  # , AUTH_URI
# from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


class TestBasket(BaseTests):

    _main_endpoint = '/basket'

    def test_01_GET_giveityourname(self, client):

        endpoint = API_URI + self._main_endpoint
        # log.info('*** Testing GET call on %s' % endpoint)
        endpoint
        assert True

        # r = client.get(endpoint)  # If NO authorization required
        # # headers, _ = self.do_login(client, None, None)
        # # r = client.get(
        # #     endpoint,
        # #     headers=headers  # If authorization required
        # # )

        # # Assert what is right or wrong
        # self.assertEqual(r.status_code, hcodes.HTTP_OK_BASIC)
        # output = self.get_content(r)

        # # pretty print data obtained from API to check the content
        # # log.pp(output)
        # assert output == 'Hello world!'
