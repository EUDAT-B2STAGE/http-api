
# import vcr
# import requests
# import json

# from restapi.tests.utilities import TestUtilities
# from restapi.tests.utilities import (
#     AUTH_URI,
#     # OK, NO_CONTENT, PARTIAL, BAD_REQUEST, FORBIDDEN, NOTFOUND, CONFLICT
#     FOUND
# )

from tests import RestTestsAuthenticatedBase
from utilities.logs import get_logger

log = get_logger(__name__)
# log.setLevel(logging.DEBUG)

# my_vcr = vcr.VCR(
#     # serializer='json',
#     cassette_library_dir='test/cassettes',
#     record_mode='once',
#     # match_on=['uri', 'method'],
# )


# class TestB2Access(TestUtilities):
class TestB2Access(RestTestsAuthenticatedBase):

    # @my_vcr.use_cassette('mytest.yaml')
    # cassette file will have the same name as the test function and will be
    # placed in the same directory as the file in which the test is defined
    # @vcr.use_cassette(
    def test_01_GET_status(self):

        # endpoint = AUTH_URI + '/askauth'
        # r = self.app.get(endpoint)
        # self.assertEqual(r.status_code, FOUND)
        # self.assertIn("Location", r.headers)

        # # TOFIX: redirect_url should be verified as a correct URL
        # redirect_url = r.headers['Location']
        # log.print(redirect_url)

        # # r = requests.get(redirect_url, allow_redirects=True)
        # # content = json.loads(r.data.decode('utf-8'))
        # # log.critical(r._content)

        pass
