# -*- coding: utf-8 -*-

"""
Move data from ingestion to production
"""
import requests

from b2stage.apis.commons.b2handle import B2HandleEndpoint
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from seadata.apis.commons.seadatacloud import Metadata as md
from restapi import decorators
from restapi.connectors.irods.client import IrodsException
from restapi.utilities.logs import log


#################
# REST CLASS
class MoveToProductionEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):

    labels = ['ingestion']
    _POST = {
        '/ingestion/<string:batch_id>/approve': {
            'summary': 'Approve files in a batch that are passing all QCs',
            'parameters': [
                {
                    'name': 'parameters',
                    'in': 'body',
                    'schema': {'$ref': '#/definitions/SeadataPost'},
                }
            ],
            'responses': {'200': {'description': 'Registration executed'}},
        }
    }

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required()
    def post(self, batch_id):

        ################
        # 0. check parameters
        json_input = self.get_input()

        params = json_input.get('parameters', {})
        if len(params) < 1:
            return self.send_errors("parameters is empty", code=400)

        files = params.get('pids', {})
        if len(files) < 1:
            return self.send_errors(
                "pids' parameter is empty list", code=400
            )

        filenames = []
        for data in files:

            if not isinstance(data, dict):
                return self.send_errors(
                    "File list contains at least one wrong entry",
                    code=400,
                )

            # print("TEST", data)
            for key in md.keys:  # + [md.tid]:
                value = data.get(key)
                if value is None:
                    error = 'Missing parameter: {}'.format(key)
                    return self.send_errors(error, code=400)

                error = None
                value_len = len(value)
                if value_len > md.max_size:
                    error = "Param '{}': exceeds size {}".format(key, md.max_size)
                elif value_len < 1:
                    error = "Param '{}': empty".format(key)
                if error is not None:
                    return self.send_errors(error, code=400)

            filenames.append(data.get(md.tid))

        ################
        # 1. check if irods path exists
        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            batch_path = self.get_irods_batch_path(imain, batch_id)
            log.debug("Batch path: {}", batch_path)

            if not imain.is_collection(batch_path):
                return self.send_errors(
                    "Batch '{}' not enabled (or no permissions)".format(batch_id),
                    code=404,
                )

            ################
            # 2. make batch_id directory in production if not existing
            prod_path = self.get_irods_production_path(imain, batch_id)
            log.debug("Production path: {}", prod_path)
            obj = self.init_endpoint()
            imain.create_collection_inheritable(prod_path, obj.username)

            ################
            # ASYNC
            log.info("Submit async celery task")
            from restapi.connectors.celery import CeleryExt

            task = CeleryExt.move_to_production_task.apply_async(
                args=[batch_id, batch_path, prod_path, json_input],
                queue='ingestion',
                routing_key='ingestion',
            )
            log.info("Async job: {}", task.id)

            return self.return_async_id(task.id)

        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=503
            )
