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
import urllib.parse
# from restapi.rest.definition import EndpointResource
from b2stage.apis.commons.cluster import ClusterContainerEndpoint
from b2stage.apis.commons.b2handle import B2HandleEndpoint
from b2stage.apis.commons import CURRENT_HTTPAPI_SERVER, API_URL
from b2stage.apis.commons.seadatacloud import ORDERS_ENDPOINT
from restapi.flask_ext.flask_celery import CeleryExt
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


def get_order_zip_file_name(order_id, restricted=False, index=None):

    index = '' if index is None else index
    label = "restricted" if restricted else "unrestricted"
    zip_file_name = 'order_%s_%s%s.zip' % (order_id, label, index)

    return zip_file_name


#################
# REST CLASSES
class DownloadBasketEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):

    def get_filename_from_type(self, order_id, ftype):
        if len(ftype) < 2:
            return None

        if ftype[0] == "0":
            restricted = False
        elif ftype[0] == "1":
            restricted = True
        else:
            log.warning("Unexpected flag in ftype %s", ftype)
            return None
        try:
            index = int(ftype[1:])
        except ValueError:
            log.warning("Unable to extract numeric index from ftype %s", ftype)

        if index == 0:
            index = None

        return get_order_zip_file_name(
            order_id,
            restricted=restricted,
            index=index)

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, order_id, ftype, code):
        """ downloading (not authenticated) """
        log.info("Order request: %s (code '%s')", order_id, code)
        json = {'order_id': order_id, 'code': code}
        msg = prepare_message(
            self, json=json, user='anonymous', log_string='start')
        log_into_queue(self, msg)

        ##################
        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_irods_order_path(imain, order_id)

        zip_file_name = self.get_filename_from_type(order_id, ftype)

        if zip_file_name is None:
            return self.send_errors("Invalid file type %s" % ftype)

        zip_ipath = path.join(order_path, zip_file_name, return_str=True)

        error = "Order '%s' not found (or no permissions)" % order_id

        log.debug("Checking zip irods path: %s", zip_ipath)
        if not imain.is_dataobject(zip_ipath):
            log.error("File not found %s", zip_ipath)
            return self.send_errors(
                {order_id: error},
                code=hcodes.HTTP_BAD_NOTFOUND
            )

        # TOFIX: we should use a database or cache to save this,
        # not irods metadata (known for low performances)
        metadata, _ = imain.get_metadata(zip_ipath)
        iticket_code = metadata.get('iticket_code')

        encoded_code = urllib.parse.quote_plus(code)

        if iticket_code != encoded_code:
            log.error("iticket code does not match %s", zip_ipath)
            return self.send_errors(
                {order_id: error},
                code=hcodes.HTTP_BAD_NOTFOUND
            )

        # NOTE: very important!
        # use anonymous to get the session here
        # because the ticket supply breaks the iuser session permissions
        icom = self.get_service_instance(
            service_name='irods', user='anonymous', password='null')
        # obj = self.init_endpoint()
        # icom = obj.icommands
        icom.ticket_supply(code)

        if not icom.test_ticket(zip_ipath):
            log.error("Invalid iticket code %s", zip_ipath)
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


class BasketEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):
    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self, order_id):
        """ listing, not downloading """

        log.debug('GET request on orders')
        msg = prepare_message(self, json=None, log_string='start')
        log_into_queue(self, msg)

        ##################
        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_irods_order_path(imain, order_id)
        log.debug("Order path: %s", order_path)
        if not imain.is_collection(order_path):
            error = "Order '%s': not existing" % order_id
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        ils = imain.list(order_path, detailed=True)

        u = get_order_zip_file_name(order_id, restricted=False, index=1)
        if u in ils:
            u = get_order_zip_file_name(order_id, restricted=False, index=None)
            ils.pop(u, None)

        r = get_order_zip_file_name(order_id, restricted=True, index=1)
        if r in ils:
            r = get_order_zip_file_name(order_id, restricted=True, index=None)
            ils.pop(r, None)

        response = []

        for _, data in ils.items():
            name = data.get('name')
            if name.endswith('_restricted.zip.bak'):
                continue

            ipath = self.join_paths([data.get('path'), name])
            metadata, _ = imain.get_metadata(ipath)
            data['URL'] = metadata.get('download')
            # obj = {
            #     'order': order_id,
            #     'file': name,
            #     'URL': metadata.get('download'),
            #     'owner': data.get('owner')
            #     'size': data.get('owner')
            # }
            # response.append(obj)
            response.append(data)

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
        main_key = 'parameters'
        params = json_input.get(main_key, {})
        if len(params) < 1:
            error = "'%s' missing" % main_key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
        # else:
        #     log.pp(params)

        ##################
        key = 'order_number'
        order_id = params.get(key)
        if order_id is None:
            error = "Order ID '%s': missing" % key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
        else:
            order_id = str(order_id)

        # ##################
        # Get filename from json input. But it has to follow a
        # specific pattern, so we ignore client input if it does not...
        filename = "order_%s_unrestricted" % order_id
        key = 'file_name'
        if key in params and not params[key] == filename:
            log.warn('Client provided wrong filename (%s), will use: %s'
                % (params[key], filename))
        params[key] = filename


        ##################
        # PIDS: can be empty if restricted
        key = 'pids'
        pids = params.get(key, [])

        ##################
        # Create the path
        log.info("Order request: %s", order_id)
        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_irods_order_path(imain, order_id)
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
            task = CeleryExt.unrestricted_order.apply_async(
                args=[order_id, order_path, zip_file_name, json_input])
            log.warning("Async job: %s", task.id)
            return self.return_async_id(task.id)

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
        encoded = urllib.parse.quote_plus(ticket)
        log.warning("Ticket: %s -> %s", ticket, encoded)
        return encoded

    def get_download(self, imain, order_id, order_path, files,
                     restricted=False, index=None):

        zip_file_name = get_order_zip_file_name(order_id, restricted, index)

        if zip_file_name not in files:
            return None

        zip_ipath = path.join(order_path, zip_file_name, return_str=True)
        log.debug("Zip irods path: %s", zip_ipath)

        code = self.no_slash_ticket(imain, zip_ipath)
        ftype = ""
        if restricted:
            ftype += "1"
        else:
            ftype += "0"
        if index is None:
            ftype += "0"
        else:
            ftype += str(index)

        route = '%s%s/%s/%s/download/%s/c/%s' % (
            CURRENT_HTTPAPI_SERVER, API_URL,
            ORDERS_ENDPOINT, order_id, ftype, code
        )

        # If metadata already exists, remove them:
        # FIXME: verify if iticket_code is set and then invalidate it
        imain.remove_metadata(zip_ipath, 'iticket_code')
        imain.remove_metadata(zip_ipath, 'download')
        ##################
        # Set the url as Metadata in the irods file
        imain.set_metadata(zip_ipath, download=route)

        # TOFIX: we should add a database or cache to save this,
        # not irods metadata (known for low performances)
        imain.set_metadata(zip_ipath, iticket_code=code)

        info = files[zip_file_name]

        return {
            'name': zip_file_name,
            'url': route,
            'size': info.get('content_length', 0)
        }

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
        order_path = self.get_irods_order_path(imain, order_id)
        log.debug("Order path: %s", order_path)

        response = []

        files_in_irods = imain.list(order_path, detailed=True)

        # Going through all possible file names of zip files

        # unrestricted zip
        # info = self.get_download(
        #     imain, order_id, order_path, files_in_irods,
        #     restricted=False, index=None)
        # if info is not None:
        #     response.append(info)

        # checking for splitted unrestricted zip
        info = self.get_download(
            imain, order_id, order_path, files_in_irods,
            restricted=False, index=1)

        # No split zip found, looking for the single unrestricted zip
        if info is None:
            info = self.get_download(
                imain, order_id, order_path, files_in_irods,
                restricted=False, index=None)
            if info is not None:
                response.append(info)
        # When found one split, looking for more:
        else:
            response.append(info)
            for index in range(2, 100):
                info = self.get_download(
                    imain, order_id, order_path, files_in_irods,
                    restricted=False, index=index)
                if info is not None:
                    response.append(info)

        # checking for splitted restricted zip
        info = self.get_download(
            imain, order_id, order_path, files_in_irods,
            restricted=True, index=1)

        # No split zip found, looking for the single restricted zip
        if info is None:
            info = self.get_download(
                imain, order_id, order_path, files_in_irods,
                restricted=True, index=None)
            if info is not None:
                response.append(info)
        # When found one split, looking for more:
        else:
            response.append(info)
            for index in range(2, 100):
                info = self.get_download(
                    imain, order_id, order_path, files_in_irods,
                    restricted=True, index=index)
                if info is not None:
                    response.append(info)

        if len(response) == 0:
            error = "Order '%s' not found (or no permissions)" % order_id
            return self.send_errors(error, code=hcodes.HTTP_BAD_NOTFOUND)

        msg = prepare_message(self, log_string='end', status='enabled')
        log_into_queue(self, msg)

        return self.force_response(response)

    def delete(self):

        json_input = self.get_input()

        # Need error codes in https://github.com/EUDAT-B2STAGE/http-api/blob/1.0.4/projects/b2stage/backend/apis/commons/seadatacloud.py
        #if not 'request_id' in json_input.keys():
        #    error = "Request ID is missing"
        #    return self.send_errors(error, code=hcodes.FOOBARBAZ)
        #if not 'parameters' in json_input.keys() and 'orders' in json_input['parameters'].keys():
        #    error = "List of orders to be deleted missing."
        #    return self.send_errors(error, code=hcodes.FOOBARBAZ)

        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_irods_order_path(imain)
        log.debug("Order path: %s", order_path)

        task = CeleryExt.delete_orders.apply_async(
            args=[order_path, json_input]
        )
        log.warning("Async job: %s", task.id)
        return self.return_async_id(task.id)
