
from tests.custom import RestTestsAuthenticatedBase


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
