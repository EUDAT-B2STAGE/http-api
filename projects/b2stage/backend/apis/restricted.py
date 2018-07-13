# -*- coding: utf-8 -*-

import json
from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi.services.uploader import Uploader
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


class Restricted(Uploader, EudatEndpoint, ClusterContainerEndpoint):
    """
    Order RESTRICTED data.
    Every DC uploads on request, it could be one or many.

    - PUT /api/restricted/<order_id> with a zip_file
    """

    # def get(self, order_id):
    #     log.info("Received a test HTTP request")

    #     # self.get_input()
    #     # log.pp(self._args, prefix_line='Parsed args')

    #     response = 'Hello world!'
    #     return self.force_response(response)

    def ingest_restricted_zip(self, icom, order_id, order_path, ipath):

        # Copy files from the B2HOST environment
        rancher = self.get_or_create_handle()

        b2safe_connvar = {
            'BATCH_SRC_PATH': order_path,
            'BATCH_DEST_PATH': ipath,
            # 'FILES': ' '.join(files),
            'IRODS_HOST': icom.variables.get('host'),
            'IRODS_PORT': icom.variables.get('port'),
            'IRODS_ZONE_NAME': icom.variables.get('zone'),
            'IRODS_USER_NAME': icom.variables.get('user'),
            'IRODS_PASSWORD': icom.variables.get('password'),
        }
        # log.pp(b2safe_connvar)

        # Launch a container to copy the data into B2HOST
        cname = 'copy_zip'  # FIXME: move me into commons/seadata*py
        cversion = '0.9'
        image_tag = '%s:%s' % (cname, cversion)
        container_name = self.get_container_name(order_id, image_tag)
        # print(container_name)
        docker_image_name = self.get_container_image(image_tag, prefix='eudat')
        log.info("Request copy2prod; image: %s" % docker_image_name)

        # remove if exists
        rancher.remove_container_by_name(container_name)
        # launch
        rancher.run(
            container_name=container_name, image_name=docker_image_name,
            private=True, pull=False,
            wait_stopped=True,
            extras={
                'environment': b2safe_connvar,
                # 'dataVolumes': [self.mount_batch_volume(batch_id)],
            },
        )
        # errors = rancher.run(
        # log.pp(errors)

    def stream_to_irods(self, icom, ipath):

        ########################
        # NOTE: only streaming is allowed, as it is more performant
        ALLOWED_MIMETYPE_UPLOAD = 'application/octet-stream'
        from flask import request
        if request.mimetype != ALLOWED_MIMETYPE_UPLOAD:
            return self.send_errors(
                "Only mimetype allowed for upload: %s"
                % ALLOWED_MIMETYPE_UPLOAD,
                code=hcodes.HTTP_BAD_REQUEST)

        try:
            # NOTE: we know this will always be Compressed Files (binaries)
            iout = icom.write_in_streaming(
                destination=ipath, force=True, binary=True)
        except BaseException as e:
            log.error("Failed streaming to iRODS: %s", e)
            return self.send_errors(
                "Failed streaming towards B2SAFE cloud",
                code=hcodes.HTTP_SERVER_ERROR)
        else:
            log.info("irods call %s", iout)
            # NOTE: permissions are inherited thanks to the POST call

    def patch(self, order_id):

        log.info('Enabling restricted: order id %s', order_id)
        json_input = self.get_input()

        ##################
        params = json_input.get('parameters', {})
        if len(params) < 1:
            error = "missing parameters"
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        # RESTRICTED PARAM
        key = 'b2access_ids'
        restricted = params.get(key, [])
        if len(restricted) < 0:
            error = "'%s' missing in JSON parameters" % key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        # Metadata handling
        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_order_path(imain, order_id)
        if not imain.is_collection(order_path):
            obj = self.init_endpoint()
            # Create the path and set permissions
            imain.create_collection_inheritable(order_path, obj.username)
            log.warning("Created %s because it did not exist", order_path)
            log.info("Assigned permissions to %s", obj.username)
            # error = "Order '%s' not found or permissions denied" % order_id
            # return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        metadata, _ = imain.get_metadata(order_path)
        log.pp(metadata)

        # Remove if existing
        key = 'restricted'
        if key in metadata:
            imain.remove_metadata(order_path, key)
            # TODO: merge with the new request
            # are they just 2 lists?
            log.info("Merge: %s and %s", metadata.get(key), restricted)
            restricted = metadata.get(key) + restricted

        # Set restricted metadata
        string = json.dumps(restricted)
        imain.set_metadata(order_path, restricted=string)
        log.debug('Flagged restricted: %s', string)

        return {'enabled': restricted}

    def put(self, order_id):
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
        order_path = self.get_order_path(imain, order_id)
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
        label = "%s_123.zip" % obj.username
        ipath = self.complete_path(order_path, label)
        self.stream_to_irods(imain, ipath)
        log.verbose("Uploaded: %s", ipath)

        ###############
        # define zip final path
        from utilities import path
        filename = 'order_%s' % order_id
        # zip_file_name = path.append_compress_extension(filename)
        zip_ipath = path.join(order_path, filename, return_str=True)

        ###############
        # launch container
        self.ingest_restricted_zip(imain, order_id, zip_ipath, ipath)

        ###############
        response = {
            'order_id': order_id,
            'status': 'filled',
        }
        return self.force_response(response)
