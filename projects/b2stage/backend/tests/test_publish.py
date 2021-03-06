"""
Run unittests inside the RAPyDo framework
"""

import io
import os

from b2stage.endpoints.commons import path
from restapi.env import Env
from restapi.tests import API_URI, AUTH_URI
from restapi.utilities.logs import log
from tests.custom import RestTestsAuthenticatedBase

maketests = (
    os.getenv("ENABLE_PUBLIC_ENDPOINT") == "1" and os.getenv("IRODS_ANONYMOUS") == "1"
)


if not maketests:
    log.info("Endpoint is not enabled!")
else:

    class TestPublish(RestTestsAuthenticatedBase):

        _anonymous_user = "anonymous"
        _main_key = "published"

        def setUp(self):

            # Call father's method
            super().setUp()

            # Remove existing files
            endpoint = f"{API_URI}/registered"  # + self._ipath
            r = self.app.delete(
                endpoint,
                data=dict(debugclean="True"),
                headers=self.__class__.auth_header,
            )
            assert r.status_code == 200

            log.info("\n### Creating a test token (ANONYMOUS IRODS user) ###")
            credentials = {
                "username": self._anonymous_user,
                "password": "notrequired",
            }
            endpoint = f"{AUTH_URI}/b2safeproxy"

            log.debug("*** Testing anonymous authentication on {}", endpoint)
            r = self.app.post(endpoint, data=credentials)
            assert r.status_code == 200
            content = self.get_content(r)
            self.save_token(content.get("token"), suffix=self._anonymous_user)

            self.irods_vars = Env.load_variables_group(prefix="irods")
            self._filename = "some_file.txt"
            home_dirname = "home"
            self._ipath = str(
                path.join(
                    path.root(),
                    self.irods_vars.get("zone"),
                    home_dirname,
                    self._irods_user,
                    self._filename,
                )
            )
            self._no_permission_path = str(
                path.join(
                    path.root(),
                    self.irods_vars.get("zone"),
                    home_dirname,
                    "nonexisting",
                )
            )
            log.debug("*** Upload a test file: {}", self._ipath)

            # Upload entity in test folder
            endpoint = f"{API_URI}/registered" + self._ipath
            r = self.app.put(
                endpoint,
                data={
                    "file": (io.BytesIO(b"just a test"), self._filename),
                    "force": True,
                },
                headers=self.__class__.auth_header,
            )
            assert r.status_code == 200

        def test_01_GET_check_if_published(self):

            endpoint = f"{API_URI}/publish"
            log.info("*** Testing GET call on {}", endpoint)

            # Current file is not published
            r = self.app.get(endpoint + self._ipath, headers=self.__class__.auth_header)
            assert r.status_code == 200
            data = self.get_content(r)
            assert data.get(self._main_key) is False

            # Random file: does not work
            r = self.app.get(
                endpoint + self._ipath + "wrong", headers=self.__class__.auth_header
            )
            assert r.status_code == 404
            error = self.get_content(r)
            assert "not existing or no permissions" in error

            # Some other user directory: does not work
            r = self.app.get(
                endpoint + self._no_permission_path, headers=self.__class__.auth_header
            )
            assert r.status_code == 404
            error = self.get_content(r)
            assert "not existing or no permissions" in error

        def test_02_PUT_publish_dataobject(self):

            endpoint = f"{API_URI}/publish"
            log.info("*** Testing PUT call on {}", endpoint)

            # Publish the file which was already uploaded
            r = self.app.put(endpoint + self._ipath, headers=self.__class__.auth_header)
            assert r.status_code == 200
            data = self.get_content(r)
            assert data.get(self._main_key) is True

            # Current file is now published
            r = self.app.get(endpoint + self._ipath, headers=self.__class__.auth_header)
            assert r.status_code == 200
            data = self.get_content(r)
            assert data.get(self._main_key) is True

            # Current file can be accessed by anonymous with /api/registered
            anonymous_endpoint = f"{API_URI}/registered"
            r = self.app.get(
                anonymous_endpoint + self._ipath,
                headers=self.__class__.auth_header_anonymous,
            )
            assert r.status_code == 200
            data = self.get_content(r)
            data_object = data.pop().get(self._filename, {})
            key = "metadata"
            assert key in data_object
            metadata = data_object.get(key)
            assert metadata.get("name") == self._filename
            assert metadata.get("object_type") == "dataobject"

            # Random file: cannot unpublish
            r = self.app.put(
                endpoint + self._ipath + "wrong", headers=self.__class__.auth_header
            )
            assert r.status_code == 404
            error = self.get_content(r)
            assert "not existing or no permissions" in error

        def test_03_POST_not_working(self):

            endpoint = f"{API_URI}/publish"
            log.info("*** Testing POST call on {}", endpoint)

            # Post method should not exist and/or not working
            r = self.app.post(
                endpoint,
                data=dict(path=self._ipath),
                headers=self.__class__.auth_header,
            )
            assert r.status_code == 404
            r = self.app.post(
                endpoint + "/some",
                data=dict(path=self._ipath),
                headers=self.__class__.auth_header,
            )
            assert r.status_code == 405

        def test_04_DELETE_unpublish_dataobject(self):

            endpoint = f"{API_URI}/publish"
            log.info("*** Testing DELETE call on {}", endpoint)

            # Publish the file which was already uploaded
            r = self.app.put(endpoint + self._ipath, headers=self.__class__.auth_header)
            assert r.status_code == 200
            data = self.get_content(r)
            assert data.get(self._main_key) is True

            # Unpublish the file which was previously published
            r = self.app.delete(
                endpoint + self._ipath, headers=self.__class__.auth_header
            )
            assert r.status_code == 200
            data = self.get_content(r)
            assert data.get(self._main_key) is False

            # Current file is now unpublished
            r = self.app.get(endpoint + self._ipath, headers=self.__class__.auth_header)
            assert r.status_code == 200
            data = self.get_content(r)
            assert data.get(self._main_key) is False

            # Current file cannot be accessed by anonymous
            anonymous_endpoint = f"{API_URI}/registered"
            r = self.app.get(
                anonymous_endpoint + self._ipath,
                headers=self.__class__.auth_header_anonymous,
            )
            assert r.status_code == 404
            errors = self.get_content(r)
            # errors is array because still returned from send_errors
            assert "you don't have privileges" in errors.pop()

            # Random file: cannot unpublish
            r = self.app.delete(
                endpoint + self._ipath + "wrong", headers=self.__class__.auth_header
            )
            assert r.status_code == 404
            error = self.get_content(r)
            assert "not existing or no permissions" in error

        def tearDown(self):

            log.debug("\n### Cleaning anonymous data ###")

            # Remove the test file
            endpoint = f"{API_URI}/registered"  # + self._ipath
            r = self.app.delete(
                endpoint,
                data=dict(debugclean="True"),
                headers=self.__class__.auth_header,
            )
            assert r.status_code == 200

            # Recover current token id
            ep = f"{AUTH_URI}/tokens"
            r = self.app.get(ep, headers=self.__class__.auth_header_anonymous)
            assert r.status_code == 200
            content = self.get_content(r)
            for element in content:
                mytoken = self.__class__.bearer_token_anonymous
                if element.get("token") == mytoken:
                    # delete only current token
                    ep += "/" + element.get("id")
                    rdel = self.app.delete(
                        ep, headers=self.__class__.auth_header_anonymous
                    )
                    assert rdel.status_code == 204

            # The end
            super().tearDown()
