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

        ###########################
        # get name from batch
        imain = self.get_service_instance(service_name='irods')
        batch_path = self.get_batch_path(imain, batch_id)
        log.info("Batch path: %s", batch_path)
        files = imain.list(batch_path)
        if len(files) != 1:
            return self.send_errors(
                'Misconfiguration for batch_id: %s' % batch_id,
                code=hcodes.HTTP_BAD_NOTFOUND
            )
        # log.pp(files)
        file_id = list(files.keys()).pop()

        ###########################
        im_prefix = 'maris'
        # im_prefix = 'eudat'
        self.get_input()
        input_json = self._args.get('input', {})

        # FIXME: only one quality check at the time on the same batch
        container_name = self.get_container_name(batch_id, qc_name)
        docker_image_name = self.get_container_image(qc_name, prefix=im_prefix)

        ###########################
        rancher = self.get_or_create_handle()
        cpath = self.get_batch_zipfile_path(batch_id, filename=file_id)
        log.verbose("Container path: %s", cpath)
        errors = rancher.run(
            container_name=container_name,
            image_name=docker_image_name,
            private=True,
            extras={
                'dataVolumes': [self.mount_batch_volume(batch_id)],
                'environment': {'BATCH_ZIPFILE_PATH': cpath}
            }
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
