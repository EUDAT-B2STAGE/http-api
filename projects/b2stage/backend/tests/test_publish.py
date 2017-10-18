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
    _main_key = 'published'

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
        home_dirname = 'home'
        self._ipath = str(path.join(
            path.root(), self.irods_vars.get('zone'),
            home_dirname, self.irods_vars.get('guest_user'), self._filename
        ))
        self._no_permission_path = str(path.join(
            path.root(), self.irods_vars.get('zone'),
            home_dirname, 'nonexisting'
        ))
        log.debug('*** Upload a test file: %s' % self._ipath)

        # Upload entity in test folder
        endpoint = self._api_uri + self._register_endpoint + self._ipath
        r = self.app.put(
            endpoint,
            data=dict(file=(io.BytesIO(b"just a test"), self._filename)),
            headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

    def test_01_GET_check_if_published(self):

        endpoint = (self._api_uri + self._main_endpoint)
        log.info('*** Testing GET call on %s' % endpoint)

        # Current file is not published
        r = self.app.get(
            endpoint + self._ipath, headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
        data = self.get_content(r)
        assert data.get(self._main_key) is False

        # Random file does not work
        r = self.app.get(
            endpoint + self._ipath + 'wrong',
            headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)
        errors = self.get_content(r, return_errors=True)
        # log.pp(errors)
        assert 'not existing' in errors.pop().get('path')

        r = self.app.get(
            endpoint + self._no_permission_path,
            headers=self.__class__.auth_header)
        self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)
        errors = self.get_content(r, return_errors=True)
        # log.pp(errors)
        assert 'no permissions' in errors.pop().get('path')

    # def test_02_POST_publish_dataobject(self):
    #     pass

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
