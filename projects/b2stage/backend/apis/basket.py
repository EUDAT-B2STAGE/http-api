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
        filenames = [
            'order_%s_unrestricted' % order_id,
            'order_%s_restricted' % order_id
        ]

        for filename in filenames:
            # filename = 'order_%s_unrestricted' % order_id
            zip_file_name = path.append_compress_extension(filename)
            zip_ipath = path.join(order_path, zip_file_name, return_str=True)

            log.debug("Checking zip irods path: %s", zip_ipath)
            if not imain.is_dataobject(zip_ipath):
                log.debug("file not found, skipping %s", zip_ipath)
                continue

            # TOFIX: we should we a database or cache to save this,
            # not irods metadata (known for low performances)
            metadata, _ = imain.get_metadata(zip_ipath)
            iticket_code = metadata.get('iticket_code')

            if iticket_code != code:
                log.debug(
                    "iticket code does not match, skipping %s", zip_ipath)
                continue

            # NOTE: very important!
            # use anonymous to get the session here
            # because the ticket supply breaks the iuser session permissions
            icom = self.get_service_instance(
                service_name='irods', user='anonymous', password='null')
            # obj = self.init_endpoint()
            # icom = obj.icommands
            icom.ticket_supply(code)

            if not icom.test_ticket(zip_ipath):

                return self.send_errors(
                    {order_id: "Invalid code"},
                    code=hcodes.HTTP_BAD_NOTFOUND
                )

            # # TODO: push pdonorio/prc
            # tickets = imain.list_tickets()
            # print(tickets)

            # iticket mod "$TICKET" add user anonymous
            # iticket mod "$TICKET" uses 1
            # iticket mod "$TICKET" expire "2018-03-23.06:50:00"

            # ##################
            # response = {order_id: 'valid'}
            # return self.force_response(response)
            headers = {
                'Content-Transfer-Encoding': 'binary',
                'Content-Disposition': "attachment; filename=%s" %
                zip_file_name,
            }
            msg = prepare_message(
                self, json=json, log_string='end', status='sent')
            log_into_queue(self, msg)
            return icom.stream_ticket(zip_ipath, headers=headers)

        error = "Order '%s' not found (or no permissions)" % order_id
        return self.send_errors(
            {order_id: error},
            code=hcodes.HTTP_BAD_NOTFOUND
        )


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

        # ##################
        key = 'file_name'
        # filename = params.get(key)
        filename = params.get(key, 'restricted')
        # if filename is None:
        #     error = "Parameter '%s' is missing" % key
        #     return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
        # elif filename != 'order_%s_unrestricted' % order_id:
        #     error = "Wrong '%s': %s" % (key, filename)
        #     return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        # ##################
        # NOTE: useless as it's the same as the request id...
        # key = 'order_number'
        # order_id = params.get(key)
        # if order_id is None:
        #     error = "Parameter '%s' is missing" % key
        #     return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        # PIDS: can be empty if restricted
        key = 'pids'
        pids = params.get(key, [])

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
            # json_input['status'] = 'exists'
            json_input['parameters'] = {'status': 'exists'}
            return json_input

        ################
        # ASYNC
        if len(pids) > 0:
            log.info("Submit async celery task")
            from restapi.flask_ext.flask_celery import CeleryExt
            task = CeleryExt.unrestricted_order.apply_async(
                args=[order_id, order_path, zip_file_name, json_input])
            log.warning("Async job: %s", task.id)
            return {'async': task.id}

        # ################
        # msg = prepare_message(self, log_string='end')
        # # msg = prepare_message(self, log_string='end', status='created')
        # msg['parameters'] = {
        #     "request_id": msg['request_id'],
        #     "zipfile_name": params['file_name'],
        #     "zipfile_count": 1,
        # }
        # log_into_queue(self, msg)

        # ################
        # # return {order_id: 'created'}
        # # json_input['status'] = 'created'
        # json_input['request_id'] = msg['request_id']
        # json_input['parameters'] = msg['parameters']
        # if len(errors) > 0:
        #     json_input['errors'] = errors

        # # call Import manager to notify
        # api = API()
        # api.post(json_input)

        return {'status': 'enabled'}

    def no_slash_ticket(self, imain, path):
        """ irods ticket for HTTP """
        # TODO: prc list tickets so we can avoid more than once
        # TODO: investigate iticket expiration
        # iticket mod Ticket_string-or-id uses/expire string-or-none

        unwanted = '/'
        ticket = unwanted
        while unwanted in ticket:
            obj = imain.ticket(path)
            ticket = obj.ticket
        import urllib.parse
        encoded = urllib.parse.quote_plus(ticket)
        log.warning("Ticket: %s -> %s", ticket, encoded)
        return encoded

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

        filenames = [
            'order_%s_unrestricted' % order_id,
            'order_%s_restricted' % order_id
        ]
        found = 0
        response = {}
        from b2stage.apis.commons import CURRENT_HTTPAPI_SERVER, API_URL
        from b2stage.apis.commons.seadatacloud import ORDERS_ENDPOINT

        for filename in filenames:
            zip_file_name = path.append_compress_extension(filename)
            zip_ipath = path.join(order_path, zip_file_name, return_str=True)
            log.debug("Zip irods path: %s", zip_ipath)

            if not imain.is_dataobject(zip_ipath):
                continue

            found += 1

            code = self.no_slash_ticket(imain, zip_ipath)

            route = '%s%s/%s/%s/download/%s' % (
                CURRENT_HTTPAPI_SERVER, API_URL,
                ORDERS_ENDPOINT, order_id, code
            )

            ##################
            # Set the url as Metadata in the irods file
            imain.set_metadata(zip_ipath, download=route)

            # TOFIX: we should we a database or cache to save this,
            # not irods metadata (known for low performances)
            imain.set_metadata(zip_ipath, iticket_code=code)

            ##################
            # response = {
            #     'GET': route,
            #     'code': code,
            # }

            response[filename] = route

        if found == 0:
            error = "Order '%s' not found (or no permissions)" % order_id
            return self.send_errors(error, code=hcodes.HTTP_BAD_NOTFOUND)

        # response = 'Work in progress'
        msg = prepare_message(self, log_string='end', status='enabled')
        log_into_queue(self, msg)

        # FIXME: REMOVE ME - BACK COMPATIBIITY CHECK
        if len(response) == 1:
            k = next(iter(response))
            response = {
                'GET': response.get(k),
                # WARNING PORCATA
                # this should work since we have only 1 element
                # so code should be the only verified file!
                'code': code,
            }
            ##################
            # response = {
            #     'GET': route,
            #     'code': code,
            # }


        return self.force_response(response)

    def delete(self, order_id):

        # FIXME: I should also revoke the task

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
        # TODO: remove the iticket?
        pass

        ##################
        # remove the path in the cloud
        imain.remove(zip_ipath)

        ##################
        response = {order_id: 'removed'}

        msg = prepare_message(self, log_string='end', status='removed')
        log_into_queue(self, msg)
        return self.force_response(response)
