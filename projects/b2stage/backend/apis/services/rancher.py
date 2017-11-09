# -*- coding: utf-8 -*-

"""
Communicating with docker via rancher
"""

from utilities.logs import get_logger
log = get_logger(__name__)


class Rancher(object):

    def __init__(self, key, secret, url):
        import gdapi
        self._client = gdapi.Client(
            url=url, access_key=key, secret_key=secret)

    def test(self):

        client = self._client
        return client.list_host()

        # client.list_project()
        # # client.list_service()

        # for element in client.list_host().data:
        #     # log.pp(element.data)
        #     print(element.id, element.uuid, element.hostname)
        #     # for key, value in element.items():
        #     #     print(key)
        # # break
        pass
