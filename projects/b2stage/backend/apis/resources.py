# -*- coding: utf-8 -*-

"""
Manage resources
"""

from restapi.rest.definition import EndpointResource
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

DOCKER_IMAGE_PREFIX = 'maris'
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

    @staticmethod
    def get_container_name(batch_id, qc_name):
        return '%s_%s' % (batch_id, qc_name.replace('_', ''))

    @staticmethod
    def get_container_image(qc_name):
        return '%s/%s' % (DOCKER_IMAGE_PREFIX, qc_name)

    def get(self, batch_id, qc_name):
        """ Check my quality check container """

        # log.info("Request for resources")
        container_name = self.get_container_name(batch_id, qc_name)
        rancher = self.get_or_create_handle()
        # resources = rancher.list()
        container = rancher.get_container_object(container_name)
        if container is None:
            return self.send_errors(
                'Quality check does not exist',
                code=hcodes.HTTP_BAD_NOTFOUND
            )

        response = {
            'batch_id': batch_id,
            'qc_name': qc_name,
            'state': container.get('state'),
            'errors': [],
        }

        if container.get('transitioning') == 'error':
            response['errors'].append(container.get('transitioningMessage'))

        """
        "state": "stopped", / error
        "firstRunningTS": 1517431685000,
        "transitioning": "no",
        "transitioning": "error",
        "transitioningMessage": "Image
        """

        return response

    def put(self, batch_id, qc_name):
        """ Launch a quality check inside a container """

        container_name = self.get_container_name(batch_id, qc_name)
        docker_image_name = self.get_container_image(qc_name)

        rancher = self.get_or_create_handle()
        errors = rancher.run(
            container_name=container_name,
            image_name=docker_image_name,
            private=True)

        response = {
            'batch_id': batch_id,
            'qc_name': qc_name,
            'status': 'executed',
        }

        if errors is not None:
            if errors.get('error', {}).get('code') == 'NotUnique':
                response['status'] = 'existing'
            else:
                response['status'] = 'failure'
        return response

    def delete(self, batch_id, qc_name):
        """
        Remove a quality check executed
        """

        container_name = self.get_container_name(batch_id, qc_name)
        rancher = self.get_or_create_handle()
        rancher.remove_container_by_name(container_name)

        response = {
            'batch_id': batch_id,
            'qc_name': qc_name,
            'status': 'removed',
        }
        return response
