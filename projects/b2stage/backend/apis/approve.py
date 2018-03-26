# -*- coding: utf-8 -*-

"""
Move data from ingestion to production
"""

#################
# IMPORTS
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
# from b2stage.apis.commons.endpoint import EudatEndpoint
from b2stage.apis.commons.b2handle import B2HandleEndpoint
# from restapi.rest.definition import EndpointResource
from b2stage.apis.commons.seadatacloud import Metadata as md
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate
from restapi.flask_ext.flask_irods.client import IrodsException
# from restapi.services.detect import detector
from utilities.logs import get_logger

#################
# INIT VARIABLES
log = get_logger(__name__)


#################
# REST CLASS
# class Approve(EndpointResource):
class MoveToProductionEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):

    # def get(self, batch_id):
    #     log.info("Received a test HTTP request")
    #     # self.get_input()
    #     # log.pp(self._args, prefix_line='Parsed args')
    #     response = 'Dummy method'
    #     return self.force_response(response)

    def pid_production(self, imain, batch_id, data):

        temp_id = data.get(md.tid)

        # ################
        # # copy file from ingestion to production
        # src_path = self.src_paths.get(temp_id)
        # log.warning("TESTING: %s (%s)", temp_id, src_path)
        dest_path = self.complete_path(self.prod_path, temp_id)
        if not imain.is_dataobject(dest_path):
            log.error("Missing: %s", dest_path)
            return None
        # log.info("Production file path: %s", dest_path)
        # imain.icopy(src_path, dest_path)

        ################
        # irule to get PID
        pid = self.pid_request(imain, dest_path)

        ################
        # irods metadata to check the PID
        metadata, _ = imain.get_metadata(dest_path)
        try:
            metadata_pid = metadata.pop('PID').strip()
        except KeyError:
            error = 'Unable to generate PID: %s/%s' % (batch_id, temp_id)
            return self.send_errors(error, code=hcodes.HTTP_SERVER_ERROR)
        else:
            if pid == metadata_pid:
                log.info("Confirmed PID: %s", pid)
            else:
                log.warning("PID unconfirmed?\n%s vs %s", pid, metadata_pid)

        # ################
        # # DEBUG extra metadata?
        # for key, value in metadata.items():
        #     if not key.lower().startswith('eudat'):
        #         print("Metadata:", key, value)
        # self.eudat_pid_fields

        # ################
        # Verify PID (b2handle)
        # TODO: re-enable, but use 'retry' python lib:
        # http://tenacity.readthedocs.io/en/latest/#examples

        # b2handle_output = None
        # counter = 0

        # while b2handle_output is None and counter < 5:
        #     counter += 1
        #     log.debug("b2handle pid test: n.%d" % counter)
        #     import time
        #     time.sleep(1)
        #     b2handle_output = self.check_pid_content(pid)

        # if b2handle_output is None:
        #     error = 'PID unverified: %s/%s = %s' % (batch_id, temp_id, pid)
        #     return self.send_errors(error, code=hcodes.HTTP_SERVER_ERROR)
        # else:
        #     log.verbose("PID verified (b2handle): %s", pid)
        #     log.pp(b2handle_output)

        ################
        # set metadata (with a prefix?)
        metadata, _ = imain.get_metadata(dest_path)
        log.pp(metadata)
        setting = False
        for key in md.keys:
            if key not in metadata:
                value = data.get(key)
                args = {'path': dest_path, key: value}
                imain.set_metadata(**args)
                setting = True
        if setting:
            log.debug("Some metadata is set")

        # ################
        # # ALL DONE: move file from ingestion to trash
        # imain.remove(src_path)
        # log.info("Source removed: %s", src_path)

        return pid

    def copy_to_production(self, icom, batch_id, files):

        # Copy files from the B2HOST environment
        rancher = self.get_or_create_handle()
        batch_dir = self.get_ingestion_path()

        b2safe_connvar = {
            'BATCH_SRC_PATH': batch_dir,
            'BATCH_DEST_PATH': self.prod_path,
            'FILES': ' '.join(files),
            'IRODS_HOST': icom.variables.get('host'),
            'IRODS_PORT': icom.variables.get('port'),
            'IRODS_ZONE_NAME': icom.variables.get('zone'),
            'IRODS_USER_NAME': icom.variables.get('user'),
            'IRODS_PASSWORD': icom.variables.get('password'),
        }
        log.pp(b2safe_connvar)

        # Launch a container to copy the data into B2HOST
        cname = 'copy_zip'
        cversion = '0.8'
        image_tag = '%s:%s' % (cname, cversion)
        container_name = self.get_container_name(batch_id, image_tag)
        print(container_name)
        docker_image_name = self.get_container_image(image_tag, prefix='eudat')
        log.info("Request copy2prod; image: %s" % docker_image_name)

        # remove if exists
        rancher.remove_container_by_name(container_name)
        # launch
        rancher.run(
            container_name=container_name, image_name=docker_image_name,
            private=True,
            wait_stopped=True,
            extras={
                'environment': b2safe_connvar,
                'dataVolumes': [self.mount_batch_volume(batch_id)],
            },
        )
        # errors = rancher.run(
        # log.pp(errors)

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def post(self, batch_id):

        # TODO: switch to list of approved files

        ################
        # 0. check parameters
        json_input = self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')

        param_key = 'parameters'
        params = json_input.get(param_key, {})
        if len(params) < 1:
            return self.send_errors(
                "'%s' is empty" % param_key, code=hcodes.HTTP_BAD_REQUEST)

        key = 'pids'
        files = params.get(key, {})
        if len(files) < 1:
            return self.send_errors(
                "'%s' parameter is empty list" % key,
                code=hcodes.HTTP_BAD_REQUEST)

        filenames = []
        for data in files:

            if not isinstance(data, dict):
                return self.send_errors(
                    "File list contains at least one wrong entry",
                    code=hcodes.HTTP_BAD_REQUEST)

            # print("TEST", data)
            for key in md.keys:  # + [md.tid]:
                value = data.get(key)
                error = None
                if value is None:
                    error = 'Missing parameter: %s' % key
                else:
                    value_len = len(value)
                if value_len > md.max_size:
                    error = "Param '%s': exceeds size %s" % (key, md.max_size)
                if value_len < 1:
                    error = "Param '%s': empty" % key
                if error is not None:
                    return self.send_errors(
                        error, code=hcodes.HTTP_BAD_REQUEST)

            filenames.append(data.get(md.tid))

        ################
        # 1. check if irods path exists
        imain = self.get_service_instance(service_name='irods')
        self.batch_path = self.get_batch_path(imain, batch_id)
        log.debug("Batch path: %s", self.batch_path)

        if not imain.is_collection(self.batch_path):
            return self.send_errors(
                "Batch '%s' not enabled (or no permissions)" % batch_id,
                code=hcodes.HTTP_BAD_REQUEST)

        ################
        # 2. make batch_id directory in production if not existing
        self.prod_path = self.get_production_path(imain, batch_id)
        log.debug("Production path: %s", self.prod_path)
        obj = self.init_endpoint()
        imain.create_collection_inheritable(self.prod_path, obj.username)

        ################
        # 3. copy files from containers to production
        self.copy_to_production(obj.icommands, batch_id, filenames)

        # ################
        # # 4. check on list of files
        # self.src_paths = {}
        # for filename in filenames:
        #     src_path = self.complete_path(self.batch_path, filename)
        #     log.info("File path: %s", src_path)
        #     self.src_paths[filename] = src_path

        #     if not imain.is_dataobject(src_path):
        #         return self.send_errors(
        #             "File '%s' not in batch '%s'" % (filename, batch_id),
        #             code=hcodes.HTTP_BAD_REQUEST)

        ################
        # 4. Request PIDs
        out_data = []
        for data in files:
            # pid, error = self.pid_production(imain, batch_id, data)
            pid = self.pid_production(imain, batch_id, data)
            if pid is None:
                log.error("Error: %s", error)
            else:
                log.info("Obtained: %s", pid)
                data['pid'] = pid
                out_data.append(data)

        ################
        # TODO: set expiration metadata on batch zip file?

        ################
        json_input[param_key] = out_data
        return json_input
