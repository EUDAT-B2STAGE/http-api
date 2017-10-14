# -*- coding: utf-8 -*-

"""
Run unittests inside the RAPyDo framework
"""

import io
import json
from tests import RestTestsAuthenticatedBase
from restapi.services.detect import detector
from utilities import path
from utilities.logs import get_logger

log = get_logger(__name__)


class TestPublish(RestTestsAuthenticatedBase):

    _auth_endpoint = '/b2safeproxy'
    _register_endpoint = '/registered'
    _main_endpoint = '/publish'
    _anonymous_user = 'anonymous'
    _root = '/'

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

        self.irods_vars = detector.services_classes.get('irods').variables
        self._filename = 'some_file.txt'
        self._ipath = str(path.join(
            self._root, self.irods_vars.get('zone'),
            'home', self.irods_vars.get('guest_user'), self._filename
        ))
        log.debug('*** Upload a test file: %s' % self._ipath)

        # Upload entity in test folder
        endpoint = self._api_uri + self._register_endpoint + self._ipath
        r = self.app.put(
            endpoint,
            data=dict(file=(io.BytesIO(b"just a test"), self._filename)),
            headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

    # def test_01_POST_publish_dataobject(self):
    #     pass

    def test_02_GET_check_if_published(self):

        endpoint = (self._api_uri + self._main_endpoint)
        log.info('*** Testing GET call on %s' % endpoint)
        r = self.app.get(
            endpoint + self._ipath, headers=self.__class__.auth_header)
        print("\n\n\n")
        log.pp(r.__dict__)
        print("\n\n\n")
        # self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        pass

        # data = json.loads(r.get_data(as_text=True))
        # # pretty print data obtained from API to check the content
        # # log.pp(data)
        # self.assertEqual(data['Response']['data'], 'Hello world!')

    # def test_03_DELETE_unpublish_dataobject(self):
    #     pass

    def tearDown(self):

        log.debug('\n### Cleaning anonymous data ###')

        # Remove the test file
        endpoint = self._api_uri + self._register_endpoint + self._ipath
        r = self.app.delete(endpoint, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

        # Recover current token id
        ep = self._auth_uri + '/tokens'
        r = self.app.get(ep, headers=self.__class__.auth_header_anonymous)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        content = self.get_content(r)
        for element in content:
            if element.get('token') == self.__class__.bearer_token_anonymous:
                # delete only current token
                ep += '/' + element.get('id')
                rdel = self.app.delete(
                    ep, headers=self.__class__.auth_header_anonymous)
                self.assertEqual(
                    rdel.status_code, self._hcodes.HTTP_OK_NORESPONSE)

        # The end
        super().tearDown()
