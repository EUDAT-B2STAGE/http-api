# -*- coding: utf-8 -*-

from tests.custom import RestTestsAuthenticatedBase
from restapi.utilities.logs import log

__authors__ = [
    'Roberto Mucci (m.dantonio@cineca.it)'
]


class TestPids(RestTestsAuthenticatedBase):

    _main_endpoint = '/pids/'

    # def tearDown(self):

    #     log.debug('### Cleaning custom data ###\n')
    #     super().tearDown()

    def test_01_GET_public_PID(self):
        """ Test directory creation: POST """

        log.info('*** Testing GET public PID')

        pid = '11100/33ac01fc-6850-11e5-b66e-e41f13eb32b2'
        pid_uri_path = 'data.repo.cineca.it:1247' + \
            '/CINECA01/home/cin_staff/rmucci00/DSI_Test/test.txt'
        wrong_pid = pid.replace('6850', 'XXXX')

        # GET URL from PID
        endpoint = self._api_uri + self._main_endpoint + pid
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 200
        # data = json.loads(r.get_data(as_text=True))
        data = self.get_content(r)
        assert data.get('URL') == 'irods://{}'.format(pid_uri_path)

        # GET URL from non existing PID
        endpoint = self._api_uri + self._main_endpoint + wrong_pid
        r = self.app.get(endpoint, headers=self.__class__.auth_header)
        assert r.status_code == 404

        # TODO: we may test right credentials using Travis secret variables
