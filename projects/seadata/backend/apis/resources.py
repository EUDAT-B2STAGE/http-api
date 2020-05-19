# -*- coding: utf-8 -*-

"""
Launch containers for quality checks in Seadata
"""
import os
import json
import time
import requests
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from b2stage.apis.commons.endpoint import MISSING_BATCH, NOT_FILLED_BATCH
from b2stage.apis.commons.endpoint import BATCH_MISCONFIGURATION
from seadata.apis.commons.cluster import INGESTION_DIR, MOUNTPOINT
from b2stage.apis.commons.b2handle import B2HandleEndpoint
from restapi import decorators
from restapi.connectors.irods.client import IrodsException
from restapi.utilities.htmlcodes import hcodes
from b2stage.apis.commons import path
from restapi.utilities.logs import log


class Resources(B2HandleEndpoint, ClusterContainerEndpoint):

    labels = ['ingestion']
    depends_on = ['RESOURCES_PROJECT']
    _GET = {
        '/ingestion/<string:batch_id>/qc/<string:qc_name>': {
            'summary': 'Resources management',
            'responses': {'200': {'description': 'unknown'}},
        }
    }
    _PUT = {
        '/ingestion/<string:batch_id>/qc/<string:qc_name>': {
            'summary': 'Launch a quality check as a docker container',
            'responses': {'200': {'description': 'unknown'}},
        }
    }
    _DELETE = {
        '/ingestion/<string:batch_id>/qc/<string:qc_name>': {
            'summary': 'Remove a quality check if existing',
            'responses': {'200': {'description': 'unknown'}},
        }
    }

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required()
    def get(self, batch_id, qc_name):
        """ Check my quality check container """

        # log.info("Request for resources")
        rancher = self.get_or_create_handle()
        container_name = self.get_container_name(batch_id, qc_name, rancher._qclabel)
        # resources = rancher.list()
        container = rancher.get_container_object(container_name)
        if container is None:
            return self.send_errors(
                'Quality check does not exist', code=hcodes.HTTP_BAD_NOTFOUND
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

        return self.response(response)

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required()
    def put(self, batch_id, qc_name):
        """ Launch a quality check inside a container """

        ###########################
        # get name from batch
        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            batch_path = self.get_irods_batch_path(imain, batch_id)
            local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
            log.info("Batch irods path: {}", batch_path)
            log.info("Batch local path: {}", local_path)
            batch_status, batch_files = self.get_batch_status(imain, batch_path, local_path)

            if batch_status == MISSING_BATCH:
                return self.send_errors(
                    "Batch '{}' not found (or no permissions)".format(batch_id),
                    code=hcodes.HTTP_BAD_NOTFOUND,
                )

            if batch_status == NOT_FILLED_BATCH:
                return self.send_errors(
                    "Batch '{}' not yet filled".format(batch_id), code=hcodes.HTTP_BAD_RESOURCE
                )

            if batch_status == BATCH_MISCONFIGURATION:
                log.error(
                    'Misconfiguration: {} files in {} (expected 1)',
                    len(batch_files),
                    batch_path,
                )
                return self.send_errors(
                    "Misconfiguration for batch_id {}".format(batch_id),
                    code=hcodes.HTTP_BAD_RESOURCE,
                )
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=hcodes.HTTP_SERVICE_UNAVAILABLE
            )

        ###################
        # Parameters (and checks)
        envs = {}
        input_json = self.get_input()

        # TODO: backdoor check - remove me
        bd = input_json.pop('eudat_backdoor', False)
        if bd:
            im_prefix = 'eudat'
        else:
            im_prefix = 'maris'
        log.debug("Image prefix: {}", im_prefix)

        # input parameters to be passed to container
        pkey = "parameters"
        param_keys = [
            "request_id",
            "edmo_code",
            "datetime",
            "api_function",
            "version",
            "test_mode",
            pkey,
        ]
        for key in param_keys:
            if key == pkey:
                continue
            value = input_json.get(key, None)
            if value is None:
                return self.send_errors(
                    'Missing JSON key: {}'.format(key), code=hcodes.HTTP_BAD_REQUEST
                )

        response = {
            'batch_id': batch_id,
            'qc_name': qc_name,
            'status': 'executed',
            'input': input_json,
        }

        ###################
        try:
            rancher = self.get_or_create_handle()
        except BaseException as e:
            log.critical(str(e))
            return self.send_errors(
                'Cannot establish a connection with Rancher',
                code=hcodes.HTTP_SERVER_ERROR,
            )

        container_name = self.get_container_name(batch_id, qc_name, rancher._qclabel)

        # Duplicated quality checks on the same batch are not allowed
        container_obj = rancher.get_container_object(container_name)
        if container_obj is not None:
            log.error("Docker container {} already exists!", container_name)
            response['status'] = 'existing'
            return self.response(errors=response, code=hcodes.HTTP_BAD_CONFLICT)

        docker_image_name = self.get_container_image(qc_name, prefix=im_prefix)

        ###########################
        # ## ENVS

        host_ingestion_path = self.get_ingestion_path_on_host(batch_id)
        container_ingestion_path = self.get_ingestion_path_in_container()

        envs['BATCH_DIR_PATH'] = container_ingestion_path
        from seadata.apis.commons.queue import QUEUE_VARS
        from seadata.apis.commons.cluster import CONTAINERS_VARS

        for key, value in QUEUE_VARS.items():
            if key in ['enable']:
                continue
            elif key == 'user':
                value = CONTAINERS_VARS.get('rabbituser')
            elif key == 'password':
                value = CONTAINERS_VARS.get('rabbitpass')
            envs['LOGS_' + key.upper()] = value
        # envs['DB_USERNAME'] = CONTAINERS_VARS.get('dbuser')
        # envs['DB_PASSWORD'] = CONTAINERS_VARS.get('dbpass')
        # envs['DB_USERNAME_EDIT'] = CONTAINERS_VARS.get('dbextrauser')
        # envs['DB_PASSWORD_EDIT'] = CONTAINERS_VARS.get('dbextrapass')

        # FOLDER inside /batches to store temporary json inputs
        # TODO: to be put into the configuration
        JSON_DIR = 'json_inputs'

        # Mount point of the json dir into the QC container
        QC_MOUNTPOINT = '/json'

        json_path_backend = os.path.join(MOUNTPOINT, INGESTION_DIR, JSON_DIR)

        if not os.path.exists(json_path_backend):
            log.info("Creating folder {}", json_path_backend)
            os.mkdir(json_path_backend)

        json_path_backend = os.path.join(json_path_backend, batch_id)

        if not os.path.exists(json_path_backend):
            log.info("Creating folder {}", json_path_backend)
            os.mkdir(json_path_backend)

        json_input_file = "input.{}.json".format(int(time.time()))
        json_input_path = os.path.join(json_path_backend, json_input_file)
        with open(json_input_path, "w+") as f:
            f.write(json.dumps(input_json))

        json_path_qc = self.get_ingestion_path_on_host(JSON_DIR)
        json_path_qc = os.path.join(json_path_qc, batch_id)
        envs['JSON_FILE'] = os.path.join(QC_MOUNTPOINT, json_input_file)

        extra_params = {
            'dataVolumes': [
                "{}:{}".format(host_ingestion_path, container_ingestion_path),
                "{}:{}".format(json_path_qc, QC_MOUNTPOINT),
            ],
            'environment': envs,
        }
        if bd:
            extra_params['command'] = ['/bin/sleep', '999999']

        # log.info(extra_params)
        ###########################
        errors = rancher.run(
            container_name=container_name,
            image_name=docker_image_name,
            private=True,
            extras=extra_params,
        )

        if errors is not None:
            if isinstance(errors, dict):
                edict = errors.get('error', {})

                # This case should never happens, since already verified before
                if edict.get('code') == 'NotUnique':
                    response['status'] = 'existing'
                    code = hcodes.HTTP_BAD_CONFLICT
                else:
                    response['status'] = 'could NOT be started'
                    response['description'] = edict
                    code = hcodes.HTTP_SERVER_ERROR
            else:
                response['status'] = 'failure'
                code = hcodes.HTTP_SERVER_ERROR
            return self.response(response, code=code)

        return self.response(response)

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required()
    def delete(self, batch_id, qc_name):
        """
        Remove a quality check executed
        """

        rancher = self.get_or_create_handle()
        container_name = self.get_container_name(batch_id, qc_name, rancher._qclabel)
        rancher.remove_container_by_name(container_name)
        # wait up to 10 seconds to verify the deletion
        log.info("Removing: {}...", container_name)
        removed = False
        for _ in range(0, 20):
            time.sleep(0.5)
            container_obj = rancher.get_container_object(container_name)
            if container_obj is None:
                log.info("{} removed", container_name)
                removed = True
                break
            else:
                log.verbose("{} still exists", container_name)

        if not removed:
            log.warning("{} still in removal status", container_name)
            response = {
                'batch_id': batch_id,
                'qc_name': qc_name,
                'status': 'not_yet_removed',
            }
        else:
            response = {'batch_id': batch_id, 'qc_name': qc_name, 'status': 'removed'}
        return self.response(response)
