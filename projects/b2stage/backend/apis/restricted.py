# -*- coding: utf-8 -*-

from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi.services.uploader import Uploader
from restapi.flask_ext.flask_celery import CeleryExt
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from utilities import htmlcodes as hcodes
from utilities import path
from utilities.logs import get_logger

log = get_logger(__name__)


class Restricted(Uploader, EudatEndpoint, ClusterContainerEndpoint):
    """
    Order RESTRICTED data.
    Every DC uploads on request, it could be one or many.

    - PUT /api/restricted/<order_id> with a zip_file
    """

    def stream_to_irods(self, icom, ipath):

        ########################
        # NOTE: only streaming is allowed, as it is more performant
        ALLOWED_MIMETYPE_UPLOAD = 'application/octet-stream'
        from flask import request
        if request.mimetype != ALLOWED_MIMETYPE_UPLOAD:
            return False, self.send_errors(
                "Only mimetype allowed for upload: %s"
                % ALLOWED_MIMETYPE_UPLOAD,
                code=hcodes.HTTP_BAD_REQUEST)

        try:
            # NOTE: we know this will always be Compressed Files (binaries)
            iout = icom.write_in_streaming(destination=ipath, force=True)

        except BaseException as e:
            log.error("Failed streaming to iRODS: %s", e)
            return False, self.send_errors(
                "Failed streaming towards B2SAFE cloud",
                code=hcodes.HTTP_SERVER_ERROR)
        else:
            log.info("irods call %s", iout)
            return True, iout
            # NOTE: permissions are inherited thanks to the POST call

    def patch(self, order_id):

        log.warning("This endpoint should be restricted to admins?")

        json_input = self.get_input()

        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_irods_order_path(imain, order_id)
        obj = self.init_endpoint()

        task = CeleryExt.create_restricted_order.apply_async(
            args=[order_id, order_path, obj.username, json_input]
        )
        log.warning("Async job: %s", task.id)
        return self.return_async_id(task.id)

    def put(self, order_id, file_id):
        """
        - Set the metadata of the folder to know that this is restricted
        - Set also the list of authorized data centers
        """

        ###############
        # json_input = self.get_input()
        # log.pp(json_input)
        # key = 'request_id'
        # order_id = json_input.get(key)
        # if order_id is None:
        #     error = "Order ID parameter '%s': missing" % key
        #     return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
        # else:
        #     order_id = str(order_id)

        ###############
        log.info("Order restricted: %s", order_id)

        # Create the path
        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_irods_order_path(imain, order_id)
        log.debug("Order path: %s", order_path)

        ###############
        error = "Order '%s' not enabled or you have no permissions" % order_id
        if not imain.is_collection(order_path):
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
        else:
            metadata, _ = imain.get_metadata(order_path)
            key = 'restricted'
            if key not in metadata:
                return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
            else:
                string = metadata.get(key)
                import json
                restricted_users = json.loads(string)
                # log.pp(restricted_users)
                if len(restricted_users) < 1:
                    return self.send_errors(
                        error, code=hcodes.HTTP_BAD_REQUEST)

        ###############
        obj = self.init_endpoint()
        if obj.username not in restricted_users:
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ###############
        # irods copy
        label = path.append_compress_extension(file_id)
        ipath = self.complete_path(order_path, label)

        if imain.exists(ipath):

            return self.send_errors(
                "%s already exist" % ipath,
                code=hcodes.HTTP_BAD_CONFLICT
            )

        uploaded, message = self.stream_to_irods(imain, ipath)

        if not uploaded:
            return message
        log.verbose("Uploaded: %s", ipath)
        log.very_verbose(message)

        ###############
        response = {
            'order_id': order_id,
            'status': 'uploaded',
        }
        return self.force_response(response)

    def post(self, order_id):

        log.warning("This endpoint should be restricted to admins?")

        json_input = self.get_input()

        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_irods_order_path(imain, order_id)

        task = CeleryExt.merge_restricted_order.apply_async(
            args=[order_id, order_path, json_input]
        )
        log.warning("Async job: %s", task.id)
        return self.return_async_id(task.id)
