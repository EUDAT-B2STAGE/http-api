"""
Launch containers for quality checks in Seadata
"""
import json
import os
import time

import requests
from b2stage.endpoints.commons import path
from b2stage.endpoints.commons.b2handle import B2HandleEndpoint
from b2stage.endpoints.commons.endpoint import (
    BATCH_MISCONFIGURATION,
    MISSING_BATCH,
    NOT_FILLED_BATCH,
)
from restapi import decorators
from restapi.exceptions import Conflict
from restapi.utilities.logs import log
from seadata.endpoints.commons.cluster import (
    INGESTION_DIR,
    MOUNTPOINT,
    ClusterContainerEndpoint,
)
from seadata.endpoints.commons.seadatacloud import EndpointsInputSchema


class Resources(B2HandleEndpoint, ClusterContainerEndpoint):

    labels = ["ingestion"]
    depends_on = ["RESOURCES_PROJECT"]

    @decorators.auth.require()
    @decorators.endpoint(
        path="/ingestion/<batch_id>/qc/<qc_name>",
        summary="Resources management",
    )
    def get(self, batch_id, qc_name):
        """Check my quality check container"""

        # log.info("Request for resources")
        rancher = self.get_or_create_handle()
        container_name = self.get_container_name(batch_id, qc_name, rancher._qclabel)
        # resources = rancher.list()
        container = rancher.get_container_object(container_name)
        if container is None:
            return self.send_errors("Quality check does not exist", code=404)

        logs = rancher.recover_logs(container_name)
        # print("TEST", container_name, tmp)
        errors_keys = ["failure", "failed", "error"]
        errors = []
        for line in logs.lower().split("\n"):
            if line.strip() == "":
                continue
            for key in errors_keys:
                if key in line:
                    errors.append(line)
                    break

        response = {
            "batch_id": batch_id,
            "qc_name": qc_name,
            "state": container.get("state"),
            "errors": errors,
        }

        if container.get("transitioning") == "error":
            response["errors"].append(container.get("transitioningMessage"))

        """
        "state": "stopped", / error
        "firstRunningTS": 1517431685000,
        "transitioning": "no",
        "transitioning": "error",
        "transitioningMessage": "Image
        """

        return self.response(response)

    @decorators.auth.require()
    @decorators.use_kwargs(EndpointsInputSchema)
    @decorators.endpoint(
        path="/ingestion/<batch_id>/qc/<qc_name>",
        summary="Launch a quality check as a docker container",
    )
    def put(self, batch_id, qc_name, **input_json):
        """Launch a quality check inside a container"""

        ###########################
        # get name from batch
        try:
            imain = self.get_main_irods_connection()
            batch_path = self.get_irods_batch_path(imain, batch_id)
            local_path = path.join(MOUNTPOINT, INGESTION_DIR, batch_id)
            log.info("Batch irods path: {}", batch_path)
            log.info("Batch local path: {}", local_path)
            batch_status, batch_files = self.get_batch_status(
                imain, batch_path, local_path
            )

            if batch_status == MISSING_BATCH:
                return self.send_errors(
                    f"Batch '{batch_id}' not found (or no permissions)",
                    code=404,
                )

            if batch_status == NOT_FILLED_BATCH:
                return self.send_errors(
                    # Bad Resource
                    f"Batch '{batch_id}' not yet filled",
                    code=410,
                )

            if batch_status == BATCH_MISCONFIGURATION:
                log.error(
                    "Misconfiguration: {} files in {} (expected 1)",
                    len(batch_files),
                    batch_path,
                )
                return self.send_errors(
                    f"Misconfiguration for batch_id {batch_id}",
                    # Bad Resource
                    code=410,
                )
        except requests.exceptions.ReadTimeout:
            return self.send_errors("B2SAFE is temporarily unavailable", code=503)

        ###################
        # Parameters (and checks)
        envs = {}

        # TODO: backdoor check - remove me
        bd = input_json.pop("eudat_backdoor", False)
        if bd:
            im_prefix = "eudat"
        else:
            im_prefix = "maris"
        log.debug("Image prefix: {}", im_prefix)

        response = {
            "batch_id": batch_id,
            "qc_name": qc_name,
            "status": "executed",
            "input": input_json,
        }

        ###################
        try:
            rancher = self.get_or_create_handle()
        except BaseException as e:
            log.critical(str(e))
            return self.send_errors(
                "Cannot establish a connection with Rancher",
                code=500,
            )

        container_name = self.get_container_name(batch_id, qc_name, rancher._qclabel)

        # Duplicated quality checks on the same batch are not allowed
        container_obj = rancher.get_container_object(container_name)
        if container_obj is not None:
            log.error("Docker container {} already exists!", container_name)
            response["status"] = "existing"
            raise Conflict(f"Docker container {container_name} already exists!")

        docker_image_name = self.get_container_image(qc_name, prefix=im_prefix)

        ###########################
        # ## ENVS

        host_ingestion_path = self.get_ingestion_path_on_host(
            rancher._localpath, batch_id
        )
        container_ingestion_path = self.get_ingestion_path_in_container()

        envs["BATCH_DIR_PATH"] = container_ingestion_path
        from seadata.endpoints.commons.cluster import CONTAINERS_VARS
        from seadata.endpoints.commons.queue import QUEUE_VARS

        for key, value in QUEUE_VARS.items():
            if key in ["enable"]:
                continue
            elif key == "user":
                value = CONTAINERS_VARS.get("rabbituser")
            elif key == "password":
                value = CONTAINERS_VARS.get("rabbitpass")
            envs["LOGS_" + key.upper()] = value
        # envs['DB_USERNAME'] = CONTAINERS_VARS.get('dbuser')
        # envs['DB_PASSWORD'] = CONTAINERS_VARS.get('dbpass')
        # envs['DB_USERNAME_EDIT'] = CONTAINERS_VARS.get('dbextrauser')
        # envs['DB_PASSWORD_EDIT'] = CONTAINERS_VARS.get('dbextrapass')

        # FOLDER inside /batches to store temporary json inputs
        # TODO: to be put into the configuration
        JSON_DIR = "json_inputs"

        # Mount point of the json dir into the QC container
        QC_MOUNTPOINT = "/json"

        json_path_backend = os.path.join(MOUNTPOINT, INGESTION_DIR, JSON_DIR)

        if not os.path.exists(json_path_backend):
            log.info("Creating folder {}", json_path_backend)
            os.mkdir(json_path_backend)

        json_path_backend = os.path.join(json_path_backend, batch_id)

        if not os.path.exists(json_path_backend):
            log.info("Creating folder {}", json_path_backend)
            os.mkdir(json_path_backend)

        json_input_file = f"input.{int(time.time())}.json"
        json_input_path = os.path.join(json_path_backend, json_input_file)
        with open(json_input_path, "w+") as f:
            f.write(json.dumps(input_json))

        json_path_qc = self.get_ingestion_path_on_host(rancher._localpath, JSON_DIR)
        json_path_qc = os.path.join(json_path_qc, batch_id)
        envs["JSON_FILE"] = os.path.join(QC_MOUNTPOINT, json_input_file)

        extra_params = {
            "dataVolumes": [
                f"{host_ingestion_path}:{container_ingestion_path}",
                f"{json_path_qc}:{QC_MOUNTPOINT}",
            ],
            "environment": envs,
        }
        if bd:
            extra_params["command"] = ["/bin/sleep", "999999"]

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
                edict = errors.get("error", {})

                # This case should never happens, since already verified before
                if edict.get("code") == "NotUnique":
                    response["status"] = "existing"
                    code = 409
                else:
                    response["status"] = "could NOT be started"
                    response["description"] = edict
                    code = 500
            else:
                response["status"] = "failure"
                code = 500
            return self.response(response, code=code)

        return self.response(response)

    @decorators.auth.require()
    @decorators.endpoint(
        path="/ingestion/<batch_id>/qc/<qc_name>",
        summary="Remove a quality check if existing",
    )
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
                log.debug("{} still exists", container_name)

        if not removed:
            log.warning("{} still in removal status", container_name)
            response = {
                "batch_id": batch_id,
                "qc_name": qc_name,
                "status": "not_yet_removed",
            }
        else:
            response = {"batch_id": batch_id, "qc_name": qc_name, "status": "removed"}
        return self.response(response)
