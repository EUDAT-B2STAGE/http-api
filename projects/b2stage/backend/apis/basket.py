# -*- coding: utf-8 -*-

"""
Orders from production data to be temporary downloadable with a zip file

# order a zip @async
POST /api/order/<OID>
    pids=[PID1, PID2, ...]

# creates the iticket/link to download
PUT /api/order/<OID> -> return iticket_code

# download the file
GET /api/order/<OID>?code=<iticket_code>

# remove the zip and the ticket
DELETE /api/order/<OID>

"""

#################
# IMPORTS
# from restapi.rest.definition import EndpointResource
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from b2stage.apis.commons.seadatacloud import ImportManagerAPI as API
from b2stage.apis.commons.b2handle import B2HandleEndpoint
# from b2stage.apis.commons.endpoint import EudatEndpoint
# from b2stage.apis.commons.seadatacloud import Metadata as md
from b2stage.apis.commons.queue import log_into_queue, prepare_message
from utilities import htmlcodes as hcodes
from restapi import decorators as decorate
from restapi.flask_ext.flask_irods.client import IrodsException
from utilities import path
from utilities.logs import get_logger

#################
# INIT VARIABLES
log = get_logger(__name__)
TMPDIR = '/tmp'


#################
# REST CLASSES


class DownloadBasketEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):
    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, order_id, code):
        """ downloading (not authenticated) """
        log.info("Order request: %s (code '%s')", order_id, code)
        json = {'order_id': order_id, 'code': code}
        msg = prepare_message(
            self, json=json, user='anonymous', log_string='start')
        log_into_queue(self, msg)

        ##################
        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_order_path(imain, order_id)

        ##################
        # verify if the path exists
        filename = 'order_%s_unrestricted' % order_id
        zip_file_name = path.append_compress_extension(filename)
        zip_ipath = path.join(order_path, zip_file_name, return_str=True)
        log.debug("Zip irods path: %s", zip_ipath)

        ##################
        error = None
        if not imain.is_dataobject(zip_ipath):
            error = "Order '%s' not found (or no permissions)" % order_id
        else:
            # NOTE: very important!
            # use anonymous to get the session here
            # because the ticket supply breaks the iuser session permissions
            icom = self.get_service_instance(
                service_name='irods', user='anonymous', password='null')
            # obj = self.init_endpoint()
            # icom = obj.icommands
            icom.ticket_supply(code)

            # code += 'error'
            if not icom.test_ticket(zip_ipath):
                error = "Invalid code"

        if error is not None:
            return self.send_errors(
                {order_id: error}, code=hcodes.HTTP_BAD_NOTFOUND)
        else:
            # # TODO: push pdonorio/prc
            # tickets = imain.list_tickets()
            # print(tickets)

            pass
            # iticket mod "$TICKET" add user anonymous
            # iticket mod "$TICKET" uses 1
            # iticket mod "$TICKET" expire "2018-03-23.06:50:00"

        # ##################
        # response = {order_id: 'valid'}
        # return self.force_response(response)
        headers = {
            'Content-Transfer-Encoding': 'binary',
            'Content-Disposition': "attachment; filename=%s.zip" % order_id,
        }
        msg = prepare_message(self, json=json, log_string='end', status='sent')
        log_into_queue(self, msg)
        return icom.stream_ticket(zip_ipath, headers=headers)


class BasketEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):
    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, order_id):
        """ listing, not downloading """

        log.debug('GET request on orders')
        msg = prepare_message(self, json=None, log_string='start')
        log_into_queue(self, msg)

        ##################
        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_order_path(imain, order_id)
        log.debug("Order path: %s", order_path)
        if not imain.is_collection(order_path):
            error = "Order '%s': not existing" % order_id
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        ils = imain.list(order_path)
        response = []

        for _, data in ils.items():
            name = data.get('name')
            ipath = self.join_paths([data.get('path'), name])
            metadata, _ = imain.get_metadata(ipath)
            # log.pp(metadata)
            obj = {
                'order': order_id,
                'file': data.get('name'),
                'URL': metadata.get('download'),
                'owner': 'NOT IMPLEMENTED YET',  # FIXME: based on irods uname?
            }
            response.append(obj)

        if len(response) < 1:
            error = "Order '%s': no files yet" % order_id
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        msg = prepare_message(self, log_string='end', status='completed')
        log_into_queue(self, msg)
        return response

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def post(self):

        ##################
        log.debug('POST request on orders')
        json_input = self.get_input()
        msg = prepare_message(self, json=json_input, log_string='start')
        log_into_queue(self, msg)

        ##################
        key = 'request_id'
        order_id = json_input.get(key)
        if order_id is None:
            error = "Order ID '%s': missing" % key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
        else:
            order_id = str(order_id)

        ##################
        main_key = 'parameters'
        params = json_input.get(main_key, {})
        if len(params) < 1:
            error = "'%s' missing" % main_key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
        # else:
        #     log.pp(params)

        ##################
        key = 'file_name'
        filename = params.get(key)
        if filename is None:
            error = "Parameter '%s' is missing" % key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
        elif filename != 'order_%s_unrestricted' % order_id:
            error = "Wrong '%s': %s" % (key, filename)
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        # ##################
        # NOTE: useless as it's the same as the request id...
        # key = 'order_number'
        # order_id = params.get(key)
        # if order_id is None:
        #     error = "Parameter '%s' is missing" % key
        #     return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        # RESTRICTED PARAM
        key = 'marine_ids'
        restricted = params.get(key, [])
        # PIDS: can be empty if restricted
        key = 'pids'
        pids = params.get(key, [])
        # # debug
        # log.pp(restricted, prefix_line='restrict')
        # log.pp(pids, prefix_line='pids')

        ##################
        # Verify marine IDs?
        key = 'restricted'
        enable_restricted = params.get(key)
        if enable_restricted == 'true' and len(restricted) < 1:
            error = "No restricted users but '%s' param is true" % key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
        if enable_restricted == 'false' and len(restricted) > 0:
            error = "Restricted users requested but '%s' param is false" % key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        # Verify pids
        files = {}
        errors = []
        for pid in pids:
            b2handle_output = self.check_pid_content(pid)
            if b2handle_output is None:
                errors.append({
                    "error": "41",  # as for Maris specs
                    "description": "PID not found",
                    "subject": pid
                })
            else:
                ipath = self.parse_pid_dataobject_path(b2handle_output)
                log.debug("PID verified: %s\n(%s)", pid, ipath)
                files[pid] = ipath
        log.verbose("PID files: %s", files)

        ##################
        # We need either Unrestricted or Restricted data to show up
        if len(files) < 1 and len(restricted) < 1:
            error = "Neither valid PIDs nor Restricted users specified"
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        # Create the path
        log.info("Order request: %s", order_id)
        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_order_path(imain, order_id)
        log.debug("Order path: %s", order_path)
        if not imain.is_collection(order_path):
            obj = self.init_endpoint()
            # Create the path and set permissions
            imain.create_collection_inheritable(order_path, obj.username)

        ##################
        # Does the zip already exists?
        # zip_file_name = path.append_compress_extension(order_id)
        zip_file_name = path.append_compress_extension(filename)
        zip_ipath = path.join(order_path, zip_file_name, return_str=True)
        if imain.is_dataobject(zip_ipath):
            # give error here
            # return {order_id: 'already exists'}
            json_input['status'] = 'exists'
            return json_input

        ##################
        metadata, _ = imain.get_metadata(order_path)
        log.pp(metadata)

        ##################
        # RESTRICTED metadata
        if enable_restricted:
            key = 'restricted'
            if key in metadata:
                imain.remove_metadata(order_path, key)
            import json
            string = json.dumps(restricted)
            # TODO: set restricted metadata
            imain.set_metadata(order_path, restricted=string)
            log.debug('Flagged restricted: %s', string)

        ##################
        local_dir = path.build([TMPDIR, order_id])
        path.create(local_dir, directory=True, force=True)

        for pid, ipath in files.items():
            # print(pid, ipath)

            # Set files to collection metadata
            if pid not in metadata:
                md = {pid: ipath}
                imain.set_metadata(order_path, **md)

            # Copy files from irods into a local TMPDIR
            filename = path.last_part(ipath)
            local_file = path.build([local_dir, filename])

            if not path.file_exists_and_nonzero(local_file):
                log.very_verbose("Copy to local: %s", local_file)
                with open(local_file, 'wb') as target:
                    with imain.get_dataobject(ipath).open('r+') as source:
                        for line in source:
                            target.write(line)

        ##################
        # Zip the dir
        zip_local_file = path.join(TMPDIR, zip_file_name)  # , return_str=True)
        # log.debug("Zip local path: %s", zip_local_file)
        if not path.file_exists_and_nonzero(zip_local_file):
            path.compress(local_dir, str(zip_local_file))
            log.info("Compressed in: %s", zip_local_file)

        ##################
        # Copy the zip into irods (force overwrite)
        imain.put(str(zip_local_file), zip_ipath)  # NOTE: always overwrite

        ################
        # return {order_id: 'created'}
        json_input['status'] = 'created'
        if len(errors) > 0:
            json_input['parameters']['errors'] = errors
        # call Import manager to notify
        api = API()
        api.post(json_input)

        msg = prepare_message(self, log_string='end', status='created')
        log_into_queue(self, msg)
        return json_input

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def put(self, order_id):

        ##################
        # imain = self.get_service_instance(service_name='irods')
        # TODO: push pdonorio/prc
        # tickets = imain.list_tickets()
        # print(tickets)
        # return "Hello"

        ##################
        log.info("Order request: %s", order_id)
        msg = prepare_message(
            self, json={'order_id': order_id}, log_string='start')
        log_into_queue(self, msg)

        # obj = self.init_endpoint()
        # icom = obj.icommands
        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_order_path(imain, order_id)
        log.debug("Order path: %s", order_path)

        ##################
        # verify if the path exists
        filename = 'order_%s_unrestricted' % order_id
        zip_file_name = path.append_compress_extension(filename)
        zip_ipath = path.join(order_path, zip_file_name, return_str=True)
        log.debug("Zip irods path: %s", zip_ipath)
        if not imain.is_dataobject(zip_ipath):
            error = "Order '%s' not found (or no permissions)" % order_id
            return self.send_errors(error, code=hcodes.HTTP_BAD_NOTFOUND)

        ##################
        # irods ticket

        # TODO: prc list tickets so we can avoid more than once
        ticket = imain.ticket(zip_ipath)
        log.warning("Ticket: %s", ticket.ticket)

        # TODO: investigate iticket expiration
        # iticket mod Ticket_string-or-id uses/expire string-or-none

        ##################
        # build URL
        from b2stage.apis.commons import CURRENT_HTTPAPI_SERVER, API_URL
        from b2stage.apis.commons.seadatacloud import ORDERS_ENDPOINT
        # GET /api/orders/?code=xxx
        import urllib.parse
        # route = '%s%s/%s/%s?code=%s' % (
        route = '%s%s/%s/%s/download/%s' % (
            CURRENT_HTTPAPI_SERVER, API_URL,
            ORDERS_ENDPOINT, order_id,
            urllib.parse.quote_plus(ticket.ticket)
        )
        # print("TEST", route)

        ##################
        # Set the url as Metadata in the irods file
        imain.set_metadata(zip_ipath, download=route)

        ##################
        # response = {'code': ticket.ticket}
        response = {
            'GET': route,
            'code': urllib.parse.quote_plus(ticket.ticket)
        }
        # response = 'Work in progress'
        msg = prepare_message(self, log_string='end', status='enabled')
        log_into_queue(self, msg)
        return self.force_response(response)

    def delete(self, order_id):

        ##################
        log.debug("DELETE request on order: %s", order_id)
        msg = prepare_message(
            self, json={'order_id': order_id}, log_string='start')
        log_into_queue(self, msg)

        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_order_path(imain, order_id)
        log.debug("Order path: %s", order_path)

        ##################
        # verify if the path exists
        filename = 'order_%s_unrestricted' % order_id
        zip_file_name = path.append_compress_extension(filename)
        zip_ipath = path.join(order_path, zip_file_name, return_str=True)
        log.debug("Zip irods path: %s", zip_ipath)
        if not imain.is_dataobject(zip_ipath):
            error = "Order '%s' not found (or no permissions)" % order_id
            return self.send_errors(error, code=hcodes.HTTP_BAD_NOTFOUND)

        ##################
        # remove the iticket
        pass

        ##################
        # remove the path in the cloud
        imain.remove(zip_ipath)

        ##################
        response = {order_id: 'removed'}

        msg = prepare_message(self, log_string='end', status='removed')
        log_into_queue(self, msg)
        return self.force_response(response)
