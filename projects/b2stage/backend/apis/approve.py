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

    # def get(self, batch_id, temp_id):
    #     log.info("Received a test HTTP request")
    #     # self.get_input()
    #     # log.pp(self._args, prefix_line='Parsed args')
    #     response = 'Dummy method: (%s, %s)' % (batch_id, temp_id)
    #     return self.force_response(response)

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def put(self, batch_id, temp_id):

        ################
        # 1. check if irods file exists

        imain = self.get_service_instance(service_name='irods')
        batch_path = self.get_batch_path(imain, batch_id)
        log.debug("Batch path: %s", batch_path)

        if not imain.is_collection(batch_path):
            return self.send_errors(
                "Batch '%s' not enabled or you have no permissions"
                % batch_id,
                code=hcodes.HTTP_BAD_REQUEST)
        src_path = self.complete_path(batch_path, temp_id)
        log.info("File path: %s", src_path)
        if not imain.is_dataobject(src_path):
            return self.send_errors(
                "File '%s' not found for batch '%s'" % (temp_id, batch_id),
                code=hcodes.HTTP_BAD_REQUEST)

        ################
        # 1.5 check parameters
        json_input = self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')
        for key in md.keys:
            value = json_input.get(key)
            error = None

            if value is None:
                error = 'Missing parameter: %s' % key
            else:
                value_len = len(value)

            if value_len > md.max_size:
                error = 'Parameter %s exceeds size %s ' % (key, md.max_size)
            if value_len < 1:
                error = 'Parameter %s empty' % key

            if error is not None:
                return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ################
        # 2. make batch_id directory in production if not existing
        prod_path = self.get_production_path(imain, batch_id)
        log.debug("Production path: %s", prod_path)
        obj = self.init_endpoint()
        imain.create_collection_inheritable(prod_path, obj.username)

        ################
        # 3. copy file from ingestion to production
        dest_path = self.complete_path(prod_path, temp_id)
        log.info("Production file path: %s", dest_path)
        imain.icopy(src_path, dest_path)

        ################
        # 4. irule to get PID
        pid = self.pid_request(imain, dest_path)
        # get the metadata to check the PID
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
                log.warning(
                    "PID unconfirmed?\nfrom rule: %s\nfrom md: %s",
                    pid, metadata_pid
                )

        # # DEBUG extra metadata?
        # for key, value in metadata.items():
        #     if not key.lower().startswith('eudat'):
        #         print("Metadata:", key, value)
        # self.eudat_pid_fields

        ################
        # 5. Verify PID (b2handle)

        b2handle_output = None
        counter = 0

        while b2handle_output is None and counter < 5:
            counter += 1
            log.debug("b2handle pid test: n.%d" % counter)
            import time
            time.sleep(1)
            b2handle_output = self.check_pid_content(pid)

        if b2handle_output is None:
            error = 'PID unverified: %s/%s = %s' % (batch_id, temp_id, pid)
            return self.send_errors(error, code=hcodes.HTTP_SERVER_ERROR)
        else:
            log.verbose("PID verified (b2handle): %s", pid)
            log.pp(b2handle_output)

        ################
        # 6. set metadata (with a prefix)
        for key in md.keys:
            value = json_input.get(key)
            args = {'path': dest_path, key: value}
            imain.set_metadata(**args)
        log.debug("Metadata set")
        # 7. check metadata ?

        ################
        # 8. ALL DONE: move file from ingestion to trash
        imain.remove(src_path)
        log.info("Source removed: %s", src_path)

        ################
        response = {'PID': pid}
        return self.force_response(response)