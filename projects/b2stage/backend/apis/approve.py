# -*- coding: utf-8 -*-

"""
Endpoint example for the RAPyDo framework
"""

#################
# IMPORTS
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from b2stage.apis.commons.endpoint import EudatEndpoint
# from restapi.rest.definition import EndpointResource
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
class Approve(EudatEndpoint, ClusterContainerEndpoint):

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
        """ {
        "cdi_n_code": "1522222",
        "format_n_code": "541555",
        "data_format_l24": "CFPOINT",
        "version": "1"
        } """

        keys = [
            "cdi_n_code", "format_n_code", "data_format_l24", "version",
        ]
        max_size = 10
        for key in keys:
            value = json_input.get(key)
            error = None

            if value is None:
                error = 'Missing parameter: %s' % key
            else:
                value_len = len(value)

            if value_len > max_size:
                error = 'Parameter %s exceeds size %s ' % (key, max_size)
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

        imain.irule()
        """
irule
    "{EUDATCreatePID(*parent_pid, *path, *ror, *fio, *fixed, *newPID)}"
    "*parent_pid=%*path=ABSOLUTE_IPATH%*ror=%*fio=%*fixed=true"
    "*newPID"
*newPID = 21.T12995/7e5300f8-1bcb-11e8-83d5-fa163e7b6737
        """

        ################
        # 5. b2handle to verify PID

        # from b2handle.handleclient import EUDATHandleClient as b2handle
        # client = b2handle.instantiate_for_read_access()
        # PID = '21.T12995/7e5300f8-1bcb-11e8-83d5-fa163e7b6737'
        # client.retrieve_handle_record(PID)

        ################
        # 6. set metadata
        ################
        # 7. check metadata ?
        ################
        # 8. ALL DONE: move file from ingestion to trash

        ################
        response = 'Dummy method.'
        # response = 'Dummy method. File list received: %s' % flist
        return self.force_response(response)
