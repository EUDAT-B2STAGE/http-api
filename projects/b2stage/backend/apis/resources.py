# -*- coding: utf-8 -*-

"""
Manage resources
"""

from restapi.rest.definition import EndpointResource
from utilities.logs import get_logger

log = get_logger(__name__)
service_name = "sqlalchemy"


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

        log.info("Request for resources")

        ###############
        rancher = self.get_or_create_handle()
        print(rancher.test())

        ###############
        # self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')

        # service_handle = self.get_service_instance(service_name)
        # log.debug("Connected to %s:\n%s", service_name, service_handle)
        # if service_handle is None:
        #     log.error('Service %s unavailable', service_name)
        #     return self.send_errors(
        #         message='Server internal error. Please contact adminers.',
        #         # code=hcodes.HTTP_BAD_NOTFOUND
        #     )

        response = 'Hello world!'
        return self.force_response(response)
