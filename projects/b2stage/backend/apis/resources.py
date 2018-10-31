# -*- coding: utf-8 -*-

"""
Launch containers for quality checks in Seadata
"""
import os
import json
import time
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from b2stage.apis.commons.cluster import INGESTION_DIR, MOUNTPOINT
from b2stage.apis.commons.b2handle import B2HandleEndpoint
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate
from restapi.flask_ext.flask_irods.client import IrodsException
from utilities.logs import get_logger

log = get_logger(__name__)


class Resources(B2HandleEndpoint, ClusterContainerEndpoint):

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
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

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def put(self, batch_id, qc_name):
        """ Launch a quality check inside a container """

        ###########################
        # get name from batch
        imain = self.get_service_instance(service_name='irods')
        batch_path = self.get_irods_batch_path(imain, batch_id)
        log.info("Batch path: %s", batch_path)
        try:
            files = imain.list(batch_path)
        except BaseException as e:
            log.warning(e.__class__.__name__)
            log.error(e)
            return self.send_errors(
                "Batch '%s' not found (or no permissions)" % batch_id,
                code=hcodes.HTTP_BAD_REQUEST
            )
        else:
            # if len(files) < 1:
            if len(files) != 1:
                log.error('Misconfiguration: %s files in %s (expected 1).' % (len(files), batch_path))
                return self.send_errors(
                    'Misconfiguration for batch_id: %s' % batch_id,
                    code=hcodes.HTTP_BAD_NOTFOUND
                )
            else:
                # log.pp(files)
                file_id = list(files.keys()).pop()

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
        log.debug("Image prefix: %s", im_prefix)

        # input parameters to be passed to container
        pkey = "parameters"
        param_keys = [
            "request_id", "edmo_code", "datetime",
            "api_function", "version", "test_mode",
            pkey
        ]
        for key in param_keys:
            if key == pkey:
                continue
            value = input_json.get(key, None)
            if value is None:
                return self.send_errors(
                    'Missing JSON key: %s' % key,
                    code=hcodes.HTTP_BAD_REQUEST
                )
            # else:
            #     envs[key.upper()] = value

        ###################
        # # check batch id also from the parameters
        # batch_j = input_json.get(pkey, {}).get("batch_number", 'UNKNOWN')
        # if batch_j != batch_id:
        #     return self.send_errors(
        #         "Wrong JSON batch id: '%s' instead of '%s'" % (
        #             batch_j, batch_id
        #         ), code=hcodes.HTTP_BAD_REQUEST
        #     )

        ###################
        # for key, value in input_json.get(pkey, {}).items():
        #     name = '%s_%s' % (pkey, key)
        #     envs[name.upper()] = value

        ###################
        # TODO: only one quality check at the time on the same batch
        # should I ps containers before launching?
        container_name = self.get_container_name(batch_id, qc_name)
        docker_image_name = self.get_container_image(qc_name, prefix=im_prefix)

        ###########################
        # ## ENVS
        rancher = self.get_or_create_handle()
        cfilepath = self.get_batch_zipfile_path(batch_id, filename=file_id)
        # log.verbose("Container path: %s", cpath)
        from utilities import path
        envs['BATCH_DIR_PATH'] = path.dir_name(cfilepath)
        from b2stage.apis.commons.queue import QUEUE_VARS
        from b2stage.apis.commons.cluster import CONTAINERS_VARS
        for key, value in QUEUE_VARS.items():
            if key in ['enable']:
                continue
            elif key == 'user':
                value = CONTAINERS_VARS.get('rabbituser')
            elif key == 'password':
                value = CONTAINERS_VARS.get('rabbitpass')
            envs['LOGS_' + key.upper()] = value
        envs['DB_USERNAME'] = CONTAINERS_VARS.get('dbuser')
        envs['DB_PASSWORD'] = CONTAINERS_VARS.get('dbpass')
        envs['DB_USERNAME_EDIT'] = CONTAINERS_VARS.get('dbextrauser')
        envs['DB_PASSWORD_EDIT'] = CONTAINERS_VARS.get('dbextrapass')

        # # SAVE JSON INPUT IN IRODS
        # # TODO: to be put into the configuration
        # tmp_json_path = self.get_irods_path(imain, 'json_inputs')

        # if not imain.exists(tmp_json_path):
        #     log.info("Creating collection %s", tmp_json_path)
        #     imain.create_directory(tmp_json_path)

        # tmp_json_path = os.path.join(tmp_json_path, batch_id)

        # if imain.exists(tmp_json_path):
        #     log.info("Removing collection %s", tmp_json_path)
        #     imain.remove(tmp_json_path, recursive=True)

        # obj = self.init_endpoint()
        # imain.create_collection_inheritable(tmp_json_path, obj.username)

        # json_input_file = "input.json"
        # json_input_path = os.path.join(tmp_json_path, json_input_file)
        # imain.create_file(json_input_path)
        # imain.write_file_content(json_input_path, json.dumps(input_json))
        # envs['JSON_FILE'] = json_input_path

        # SAVE JSON INPUT ON FILE SYSTEM

        # FOLDER inside /batches to store temporary json inputs
        # TODO: to be put into the configuration
        JSON_DIR = 'json_inputs'

        # Mount point of the json dir into the QC container
        QC_MOUNTPOINT = '/json'

        tmp_json_path = os.path.join(MOUNTPOINT, INGESTION_DIR, JSON_DIR)

        if not os.path.exists(tmp_json_path):
            log.info("Creating folder %s", tmp_json_path)
            os.mkdir(tmp_json_path)

        tmp_json_path = os.path.join(tmp_json_path, batch_id)

        if not os.path.exists(tmp_json_path):
            log.info("Creating folder %s", tmp_json_path)
            os.mkdir(tmp_json_path)

        json_input_file = "input.%s.json" % int(time.time())
        json_input_path = os.path.join(tmp_json_path, json_input_file)
        with open(json_input_path, "w+") as f:
            f.write(json.dumps(input_json))
        # envs['JSON_FILE'] = json_input_path
        envs['JSON_FILE'] = os.path.join(QC_MOUNTPOINT, json_input_file)

        # Temporary added, to be removed once JSON_FILE will work
        envs['JSON_INPUT'] = json.dumps(input_json)

        ###########################
        errors = rancher.run(
            container_name=container_name,
            image_name=docker_image_name,
            private=True,
            extras={
                'dataVolumes': [
                    self.mount_batch_volume(batch_id),
                    "%s:%s" % (tmp_json_path, QC_MOUNTPOINT)

                ],
                'environment': envs,
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
                    code = hcodes.HTTP_BAD_CONFLICT
                else:
                    response['status'] = 'could NOT be started'
                    response['description'] = edict
                    code = hcodes.HTTP_BAD_REQUEST
            else:
                response['status'] = 'failure'
                code = hcodes.HTTP_BAD_REQUEST
            return self.force_response(
                response, errors=[response['status']], code=code)

        return response

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def delete(self, batch_id, qc_name):
        """
        Remove a quality check executed
        """

        container_name = self.get_container_name(batch_id, qc_name)
        rancher = self.get_or_create_handle()
        rancher.remove_container_by_name(container_name)
        log.info("About to remove: %s", container_name)

        response = {
            'batch_id': batch_id,
            'qc_name': qc_name,
            'status': 'removed',
        }
        return response
