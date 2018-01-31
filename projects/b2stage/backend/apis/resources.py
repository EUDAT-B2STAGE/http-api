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
            # log.pp(params)
            self._handle = Rancher(**params)
        return self._handle

    def get(self, batch_id, qc_name):
        """ Check my quality check container """

        # log.info("Request for resources")

        # rancher = self.get_or_create_handle()
        # resources = rancher.list()

        # return self.force_response(resources)
        return "Hello"

    def post(self, batch_id, qc_name):
        """ run a container """

        if 'docker_example_' not in qc_name:
            return self.send_errors("Only image allowed is 'docker_example'")

        # self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')
        # docker_image_name = self._args.get('image')
        container_name = 'qc1'
        docker_image_name = 'maris/docker_example_vs_17_v3'

        rancher = self.get_or_create_handle()
        errors = rancher.run(
            container_name=container_name,
            image_name=docker_image_name,
            private=True)

        if errors is None:
            # return 'Executed: %s' % container_name
            return {'qcid': container_name}
        else:
            if errors.get('error', {}).get('code') == 'NotUnique':
                return self.send_errors('Already executed')
            else:
                return self.send_errors('Failed to launch')

    # def put(self, container_id):
    #     """
    #     Execute a command inside a running container
    #     """
    #     pass

    def delete(self, batch_id, qc_name):
        """
        Remove a quality check executed
        """

        rancher = self.get_or_create_handle()
        qc_name = 'qc1'
        rancher.remove_container_by_name(qc_name)
        return {'removed': qc_name}
