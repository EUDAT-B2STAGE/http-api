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

log = get_logger(__name__)


#################
# REST CLASS
# class Approve(EndpointResource):
class MoveToProductionEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def post(self, batch_id):

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
        self.batch_path = self.get_irods_batch_path(imain, batch_id)
        log.debug("Batch path: %s", self.batch_path)

        if not imain.is_collection(self.batch_path):
            return self.send_errors(
                "Batch '%s' not enabled (or no permissions)" % batch_id,
                code=hcodes.HTTP_BAD_REQUEST)

        ################
        # 2. make batch_id directory in production if not existing
        self.prod_path = self.get_irods_production_path(imain, batch_id)
        log.debug("Production path: %s", self.prod_path)
        obj = self.init_endpoint()
        imain.create_collection_inheritable(self.prod_path, obj.username)

        ################
        # ASYNC
        log.info("Submit async celery task")
        from restapi.flask_ext.flask_celery import CeleryExt
        task = CeleryExt.move_to_production_task.apply_async(
            args=[batch_id, self.prod_path, json_input])
        log.warning("Async job: %s", task.id)

        return self.return_async_id(task.id)
