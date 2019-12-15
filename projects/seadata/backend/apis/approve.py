# -*- coding: utf-8 -*-

"""
Move data from ingestion to production
"""
import requests

from b2stage.apis.commons.b2handle import B2HandleEndpoint
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from seadata.apis.commons.seadatacloud import Metadata as md
from restapi import decorators as decorate
from restapi.protocols.bearer import authentication
from restapi.flask_ext.flask_irods.client import IrodsException
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


#################
# REST CLASS
class MoveToProductionEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):

    # schema_expose = True
    labels = ['seadatacloud', 'ingestion']
    depends_on = ['SEADATA_PROJECT']
    POST = {
        '/ingestion/<string:batch_id>/approve': {
            'custom': {},
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

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    @authentication.required()
    def post(self, batch_id):

        ################
        # 0. check parameters
        json_input = self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')

        params = json_input.get('parameters', {})
        if len(params) < 1:
            return self.send_errors("parameters is empty", code=hcodes.HTTP_BAD_REQUEST)

        files = params.get('pids', {})
        if len(files) < 1:
            return self.send_errors(
                "pids' parameter is empty list", code=hcodes.HTTP_BAD_REQUEST
            )

        filenames = []
        for data in files:

            if not isinstance(data, dict):
                return self.send_errors(
                    "File list contains at least one wrong entry",
                    code=hcodes.HTTP_BAD_REQUEST,
                )

            # print("TEST", data)
            for key in md.keys:  # + [md.tid]:
                value = data.get(key)
                if value is None:
                    error = 'Missing parameter: {}'.format(key)
                    return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

                error = None
                value_len = len(value)
                if value_len > md.max_size:
                    error = "Param '{}': exceeds size {}".format(key, md.max_size)
                elif value_len < 1:
                    error = "Param '{}': empty".format(key)
                if error is not None:
                    return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

            filenames.append(data.get(md.tid))

        ################
        # 1. check if irods path exists
        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            self.batch_path = self.get_irods_batch_path(imain, batch_id)
            log.debug("Batch path: {}", self.batch_path)

            if not imain.is_collection(self.batch_path):
                return self.send_errors(
                    "Batch '{}' not enabled (or no permissions)".format(batch_id),
                    code=hcodes.HTTP_BAD_NOTFOUND,
                )

            ################
            # 2. make batch_id directory in production if not existing
            self.prod_path = self.get_irods_production_path(imain, batch_id)
            log.debug("Production path: {}", self.prod_path)
            obj = self.init_endpoint()
            imain.create_collection_inheritable(self.prod_path, obj.username)

            ################
            # ASYNC
            log.info("Submit async celery task")
            from restapi.flask_ext.flask_celery import CeleryExt

            task = CeleryExt.move_to_production_task.apply_async(
                args=[batch_id, self.prod_path, json_input],
                queue='ingestion',
                routing_key='ingestion',
            )
            log.info("Async job: {}", task.id)

            return self.return_async_id(task.id)

        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=hcodes.HTTP_SERVICE_UNAVAILABLE
            )
