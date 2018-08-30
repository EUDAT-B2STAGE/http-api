# -*- coding: utf-8 -*-

"""
Launch containers for quality checks in Seadata
"""

from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate
from restapi.flask_ext.flask_irods.client import IrodsException
from utilities.logs import get_logger
from b2stage.apis.commons.queue import log_into_queue, prepare_message

log = get_logger(__name__)


class Resources(ClusterContainerEndpoint):

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

        # Log start into RabbitMQ
        log.info('Received request to run qc "%s" on batch "%s"' % (qc_name, batch_id))
        log_msg = prepare_message(self,
            log_string='start'
        )
        log_into_queue(self, log_msg)

        ###########################
        # get name from batch
        imain = self.get_service_instance(service_name='irods')
        batch_path = self.get_batch_path(imain, batch_id)
        log.info("Batch path: %s", batch_path)
        try:
            files = imain.list(batch_path)

        # Failure: Batch not found or no permissions
        # Log to RabbitMQ and return error code
        except BaseException as e:
            log.warning(e.__class__.__name__)
            log.error(e)
            err_msg = ("Batch '%s' not found (or no permissions)" %
                batch_id)
            log_msg = prepare_message(self,
                log_string='failure',
                error = err_msg
            )
            log_into_queue(self, log_msg)
            return self.send_errors(err_msg,
                code=hcodes.HTTP_BAD_REQUEST
            )
        else:

            # Failure: Not exactly 1 file:
            # Log to RabbitMQ and return error code
            if len(files) != 1:
                err_msg = ('Misconfiguration for batch %s: %s files in %s (expected 1).'
                    % (batch_id, len(files), batch_path))
                log_msg = prepare_message(self,
                    log_string='failure',
                    error = err_msg
                )
                log_into_queue(self, log_msg)
                return self.send_errors(err_msg,
                    code=hcodes.HTTP_BAD_NOTFOUND
                )

            else:
                # log.pp(files)
                file_id = list(files.keys()).pop()

        ###################
        # Parameters (and checks)
        envs = {}
        input_json = self.get_input()
        # input_json = self._args.get('input', {})

        # backdoor check
        bd = input_json.pop('eudat_backdoor', False)  # TODO: remove me
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

            # Failure: Missing JSON key
            # Log to RabbitMQ and return error code
            if value is None:
                err_msg = ('Missing JSON key: %s' % key)
                log_msg = prepare_message(self,
                    log_string='failure',
                    error = err_msg
                )
                log_into_queue(self, log_msg)
                return self.send_errors(err_msg,
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
        import json
        envs['JSON_INPUT'] = json.dumps(input_json)
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

        # # envs['BATCH_ZIPFILE_PATH'] = cpath
        # log.pp(envs)
        # return 'Hello'

        ###########################
        errors = rancher.run(
            container_name=container_name,
            image_name=docker_image_name,
            private=True,
            extras={
                'dataVolumes': [self.mount_batch_volume(batch_id)],
                'environment': envs,
            }
        )

        response = {
            'batch_id': batch_id,
            'qc_name': qc_name,
            'status': 'executed', # TODO started
            'input': input_json,
        }

        if errors is None:
            logstring = 'end'
        else:
            logstring = 'failure'
            if isinstance(errors, dict):
                edict = errors.get('error', {})
                # print("TEST", edict)
                if edict.get('code') == 'NotUnique':
                    response['status'] = 'existing' # TODO this means container exists! not result exists!
                else:
                    response['status'] = 'could NOT be started'
                    response['description'] = edict
            else:
                response['status'] = 'failure'

        # Log end into RabbitMQ
        log_msg = prepare_message(self,
            log_string=logstring,
            status = response['status']
        )
        log_into_queue(self, log_msg)

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
