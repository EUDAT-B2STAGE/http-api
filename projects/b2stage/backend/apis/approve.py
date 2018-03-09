# -*- coding: utf-8 -*-

"""
Endpoint example for the RAPyDo framework
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
class Approve(B2HandleEndpoint, ClusterContainerEndpoint):

    def get(self, batch_id, temp_id):
        log.info("Received a test HTTP request")
        # self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')
        response = 'Dummy method: (%s, %s)' % (batch_id, temp_id)
        return self.force_response(response)

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def put(self, batch_id, temp_id):

        log.info("Received a test HTTP request")

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

        # EUDAT RULE for PID
        out_name = 'newPID'
        inputs = {
            '*path': '"%s"' % dest_path,
            '*fixed': '"true"',
            # empty variables
            '*parent_pid': '""',
            '*ror': '""',
            '*fio': '""',
        }
        body = """
            EUDATCreatePID(*parent_pid, *path, *ror, *fio, *fixed, *%s)
        """ % out_name
        imain.irule('get_pid', body, inputs, out_name)

        # # NOTE: output not working yet:
        # output = imain.irule('get_pid', body, inputs, out_name)
        # print("TEST", output)
        # # https://github.com/irods/python-irodsclient/issues/119
        # # log.pp(output)

        # get the metadata to check the PID
        metadata, _ = imain.get_metadata(dest_path)

        try:
            pid = metadata.pop('PID')
        except KeyError:
            error = 'Unable to generate PID: %s/%s' % (batch_id, temp_id)
            # log.error(error)
            return self.send_errors(error, code=hcodes.HTTP_SERVER_ERROR)
        else:
            log.info("PID: %s", pid)

        # # DEBUG extra metadata?
        # for key, value in metadata.items():
        #     if not key.lower().startswith('eudat'):
        #         print("Metadata:", key, value)
        # self.eudat_pid_fields

        ################
        # 5. Verify PID (b2handle)

        # FIXME: better max retries: 5
        import time
        time.sleep(3)

        out = self.check_pid_content(pid)

        if out is None:
            error = 'Cannot confirm PID: %s/%s = %s' % (batch_id, temp_id, pid)
            # log.error(error)
            return self.send_errors(error, code=hcodes.HTTP_SERVER_ERROR)
        else:
            log.verbose("PID %s verified", pid)
            log.pp(out)

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
