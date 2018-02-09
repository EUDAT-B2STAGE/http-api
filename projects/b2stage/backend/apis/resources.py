# -*- coding: utf-8 -*-

"""
Launch containers for quality checks in Seadata
"""

from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


class Resources(ClusterContainerEndpoint):

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

        logs = rancher.recover_logs(container_name)
        # print("TEST", container_name, tmp)
        errors_keys = ['failure', 'failed', 'error']
        errors = []
        for line in logs.lower().split('\n'):
            if line.strip() == '':
                continue
            for key in errors_keys:
                if key in line:
                    errors.append(line)
                    break

        response = {
            'batch_id': batch_id,
            'qc_name': qc_name,
            'state': container.get('state'),
            'errors': errors,
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

        self.get_input()
        input_json = self._args.get('input', {})

        container_name = self.get_container_name(batch_id, qc_name)
        docker_image_name = self.get_container_image(qc_name, prefix='maris')

        ###########################
        rancher = self.get_or_create_handle()
        errors = rancher.run(
            container_name=container_name,
            image_name=docker_image_name,
            private=True,
            # extras={'environment': b2safe_connvar},
        )

        response = {
            'batch_id': batch_id,
            'qc_name': qc_name,
            'status': 'executed',
            'input': input_json,
        }

        if errors is not None:
            if isinstance(errors, dict):
                edict = errors.get('error', {})
                # print("TEST", edict)
                if edict.get('code') == 'NotUnique':
                    response['status'] = 'existing'
                else:
                    response['status'] = 'could NOT be started'
                    response['description'] = edict
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
