# -*- coding: utf-8 -*-

"""
Run unittests inside the RAPyDo framework
"""

import os
import io
import json
from tests import RestTestsAuthenticatedBase
from restapi.services.detect import detector
from utilities import path
from utilities.logs import get_logger

log = get_logger(__name__)

maketests = \
    os.environ.get('ENABLE_PUBLIC_ENDPOINT') == '1' and \
    os.environ.get('IRODS_ANONYMOUS') == '1'


if not maketests:
    log.info('Endpoint is not enabled!')
else:

    class TestPublish(RestTestsAuthenticatedBase):

        _auth_endpoint = '/b2safeproxy'
        _register_endpoint = '/registered'
        _main_endpoint = '/publish'
        _anonymous_user = 'anonymous'
        _main_key = 'published'

        def setUp(self):

            # Call father's method
            super().setUp()

            # Remove existing files
            endpoint = self._api_uri + self._register_endpoint  # + self._ipath
            r = self.app.delete(
                endpoint,
                data=dict(debugclean='True'),
                headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

            log.info("\n### Creating a test token (ANONYMOUS IRODS user) ###")
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

            endpoint = self._api_uri + self._main_endpoint
            log.info('*** Testing GET call on %s' % endpoint)

            # Current file is not published
            r = self.app.get(
                endpoint + self._ipath, headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
            data = self.get_content(r)
            assert data.get(self._main_key) is False

            # Random file: does not work
            r = self.app.get(
                endpoint + self._ipath + 'wrong',
                headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)
            errors = self.get_content(r, return_errors=True)
            # log.pp(errors)
            assert 'not existing' in errors.pop().get('path')

            # Some other user directory: does not work
            r = self.app.get(
                endpoint + self._no_permission_path,
                headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)
            errors = self.get_content(r, return_errors=True)
            # log.pp(errors)
            assert 'no permissions' in errors.pop().get('path')

        def test_02_PUT_publish_dataobject(self):

            endpoint = self._api_uri + self._main_endpoint
            log.info('*** Testing PUT call on %s' % endpoint)

            # Publish the file which was already uploaded
            r = self.app.put(
                endpoint + self._ipath,
                headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
            data = self.get_content(r)
            assert data.get(self._main_key) is True

            # Current file is now published
            r = self.app.get(
                endpoint + self._ipath, headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
            data = self.get_content(r)
            assert data.get(self._main_key) is True

            # Current file can be accessed by anonymous with /api/registered
            anonymous_endpoint = self._api_uri + self._register_endpoint
            r = self.app.get(
                anonymous_endpoint + self._ipath,
                headers=self.__class__.auth_header_anonymous)
            self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
            data = self.get_content(r)
            data_object = data.pop().get(self._filename, {})
            key = 'metadata'
            self.assertIn(key, data_object)
            metadata = data_object.get(key)
            self.assertEqual(metadata.get('name'), self._filename)
            self.assertEqual(metadata.get('object_type'), 'dataobject')

            # Random file: cannot unpublish
            r = self.app.put(
                endpoint + self._ipath + 'wrong',
                headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)
            errors = self.get_content(r, return_errors=True)
            assert 'not existing' in errors.pop().get('path')

        def test_03_POST_not_working(self):

            endpoint = self._api_uri + self._main_endpoint
            log.info('*** Testing POST call on %s' % endpoint)

            # Post method should not exist and/or not working
            r = self.app.post(
                endpoint, data=dict(path=self._ipath),
                headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)
            r = self.app.post(
                endpoint + '/some', data=dict(path=self._ipath),
                headers=self.__class__.auth_header)
            self.assertEqual(
                r.status_code, self._hcodes.HTTP_BAD_METHOD_NOT_ALLOWED)

        def test_04_DELETE_unpublish_dataobject(self):

            endpoint = self._api_uri + self._main_endpoint
            log.info('*** Testing DELETE call on %s' % endpoint)

            # Publish the file which was already uploaded
            r = self.app.put(
                endpoint + self._ipath,
                headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
            data = self.get_content(r)
            assert data.get(self._main_key) is True

            # Unpublish the file which was previously published
            r = self.app.delete(
                endpoint + self._ipath,
                headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
            data = self.get_content(r)
            assert data.get(self._main_key) is False

            # Current file is now unpublished
            r = self.app.get(
                endpoint + self._ipath, headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
            data = self.get_content(r)
            assert data.get(self._main_key) is False

            # Current file cannot be accessed by anonymous
            anonymous_endpoint = self._api_uri + self._register_endpoint
            r = self.app.get(
                anonymous_endpoint + self._ipath,
                headers=self.__class__.auth_header_anonymous)
            self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)
            errors = self.get_content(r, return_errors=True)
            # log.pp(errors)
            assert "you don't have privileges" in errors.pop()

            # Random file: cannot unpublish
            r = self.app.delete(
                endpoint + self._ipath + 'wrong',
                headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_BAD_NOTFOUND)
            errors = self.get_content(r, return_errors=True)
            assert 'not existing' in errors.pop().get('path')

        def tearDown(self):

            log.debug('\n### Cleaning anonymous data ###')

            # Remove the test file
            endpoint = self._api_uri + self._register_endpoint  # + self._ipath
            r = self.app.delete(
                endpoint,
                data=dict(debugclean='True'),
                headers=self.__class__.auth_header)
            self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)

            # Recover current token id
            ep = self._auth_uri + '/tokens'
            r = self.app.get(ep, headers=self.__class__.auth_header_anonymous)
            self.assertEqual(r.status_code, self._hcodes.HTTP_OK_BASIC)
            content = self.get_content(r)
            for element in content:
                mytoken = self.__class__.bearer_token_anonymous
                if element.get('token') == mytoken:
                    # delete only current token
                    ep += '/' + element.get('id')
                    rdel = self.app.delete(
                        ep, headers=self.__class__.auth_header_anonymous)
                    self.assertEqual(
                        rdel.status_code, self._hcodes.HTTP_OK_NORESPONSE)

            # The end
            super().tearDown()
