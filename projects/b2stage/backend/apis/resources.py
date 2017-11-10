# -*- coding: utf-8 -*-

"""
Manage resources
"""

from restapi.rest.definition import EndpointResource
from utilities.logs import get_logger

log = get_logger(__name__)


class Resources(EndpointResource):

    def custom_init(self):
        """ It gets called every time a new request is executed """
        self._handle = None
        self._credentials = {}

        self.load_credentials()
        self.get_or_create_handle()

    def load_credentials(self):

        if len(self._credentials) < 1:
            from restapi.services.detect import detector
            self._credentials = detector.load_group(label='resources')
        return self._credentials

    def get_or_create_handle(self):

        if self._handle is None:
            from b2stage.apis.services.rancher import Rancher
            params = self.load_credentials()
            self._handle = Rancher(**params)
        return self._handle

    def get(self):
        """ list resources """

        log.info("Request for resources")

        rancher = self.get_or_create_handle()
        resources = rancher.list()

        return self.force_response(resources)

    def post(self):
        """ run a container """

        self.get_input()
        log.pp(self._args, prefix_line='Parsed args')

        rancher = self.get_or_create_handle()
        rancher.test()
        return "Hello!"

    def put(self, container_id):
        """
        Execute a command inside a running container
        """
        pass
