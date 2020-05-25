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
import requests

# from restapi.rest.definition import EndpointResource
from seadata.apis.commons.cluster import ClusterContainerEndpoint
from seadata.apis.commons.cluster import ORDERS_DIR, MOUNTPOINT
from b2stage.apis.commons.b2handle import B2HandleEndpoint
from b2stage.apis.commons import CURRENT_HTTPAPI_SERVER, API_URL
from seadata.apis.commons.seadatacloud import ORDERS_ENDPOINT
from restapi import decorators
from restapi.connectors.celery import CeleryExt
from seadata.apis.commons.queue import log_into_queue, prepare_message
from restapi.connectors.irods.client import IrodsException
from b2stage.apis.commons import path
from restapi.utilities.logs import log

from irods.exception import NetworkException

TMPDIR = '/tmp'


def get_order_zip_file_name(order_id, restricted=False, index=None):

    index = '' if index is None else index
    label = "restricted" if restricted else "unrestricted"
    zip_file_name = 'order_{}_{}{}.zip'.format(order_id, label, index)

    return zip_file_name


#################
# REST CLASSES
class DownloadBasketEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):

    labels = ['order']
    _GET = {
        '/orders/<string:order_id>/download/<string:ftype>/c/<string:code>': {
            'summary': 'Download an order',
            'responses': {
                '200': {'description': 'The order with all files compressed'},
                '404': {'description': 'Order does not exist'},
            },
        }
    }

    def get_filename_from_type(self, order_id, ftype):
        if len(ftype) < 2:
            return None

        if ftype[0] == "0":
            restricted = False
        elif ftype[0] == "1":
            restricted = True
        else:
            log.warning("Unexpected flag in ftype {}", ftype)
            return None
        try:
            index = int(ftype[1:])
        except ValueError:
            log.warning("Unable to extract numeric index from ftype {}", ftype)

        if index == 0:
            index = None

        return get_order_zip_file_name(order_id, restricted=restricted, index=index)

    @decorators.catch_errors(exception=IrodsException)
    def get(self, order_id, ftype, code):
        """ downloading (not authenticated) """
        log.info("Order request: {} (code '{}')", order_id, code)
        json = {'order_id': order_id, 'code': code}
        msg = prepare_message(self, json=json, user='anonymous', log_string='start')
        log_into_queue(self, msg)

        log.info("DOWNLOAD DEBUG 1: {} (code '{}')", order_id, code)

        ##################
        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            log.info("DOWNLOAD DEBUG 2: {} (code '{}')", order_id, code)
            order_path = self.get_irods_order_path(imain, order_id)
            log.info("DOWNLOAD DEBUG 3: {} (code '{}') - {}", order_id, code, order_path)

            zip_file_name = self.get_filename_from_type(order_id, ftype)

            if zip_file_name is None:
                return self.send_errors("Invalid file type {}".format(ftype))

            zip_ipath = path.join(order_path, zip_file_name, return_str=True)

            error = "Order '{}' not found (or no permissions)".format(order_id)

            log.debug("Checking zip irods path: {}", zip_ipath)
            log.info("DOWNLOAD DEBUG 4: {} (code '{}') - {}", order_id, code, zip_ipath)
            if not imain.is_dataobject(zip_ipath):
                log.error("File not found {}", zip_ipath)
                return self.send_errors({order_id: error}, code=404)

            log.info("DOWNLOAD DEBUG 5: {} (code '{}')", order_id, code)

            # TOFIX: we should use a database or cache to save this,
            # not irods metadata (known for low performances)
            metadata, _ = imain.get_metadata(zip_ipath)
            log.info("DOWNLOAD DEBUG 6: {} (code '{}')", order_id, code)
            iticket_code = metadata.get('iticket_code')
            log.info("DOWNLOAD DEBUG 7: {} (code '{}')", order_id, code)

            encoded_code = urllib.parse.quote_plus(code)
            log.info("DOWNLOAD DEBUG 8: {} (code '{}')", order_id, code)

            if iticket_code != encoded_code:
                log.error("iticket code does not match {}", zip_ipath)
                return self.send_errors({order_id: error}, code=404)

            # NOTE: very important!
            # use anonymous to get the session here
            # because the ticket supply breaks the iuser session permissions
            icom = self.get_service_instance(
                service_name='irods',
                user='anonymous',
                password='null',
                authscheme='credentials',
            )
            log.info("DOWNLOAD DEBUG 9: {} (code '{}')", order_id, code)
            # obj = self.init_endpoint()
            # icom = obj.icommands
            icom.ticket_supply(code)

            log.info("DOWNLOAD DEBUG 10: {} (code '{}')", order_id, code)
            if not icom.test_ticket(zip_ipath):
                log.error("Invalid iticket code {}", zip_ipath)
                return self.send_errors(
                    {order_id: "Invalid code"}, code=404
                )

            # tickets = imain.list_tickets()
            # print(tickets)

            # iticket mod "$TICKET" add user anonymous
            # iticket mod "$TICKET" uses 1
            # iticket mod "$TICKET" expire "2018-03-23.06:50:00"

            headers = {
                'Content-Transfer-Encoding': 'binary',
                'Content-Disposition': "attachment; filename={}".format(zip_file_name),
            }
            msg = prepare_message(self, json=json, log_string='end', status='sent')
            log_into_queue(self, msg)
            log.info("DOWNLOAD DEBUG 11: {} (code '{}')", order_id, code)
            return icom.stream_ticket(zip_ipath, headers=headers)
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=503
            )


class BasketEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):

    labels = ['order']
    _GET = {
        '/orders/<string:order_id>': {
            'summary': 'List orders',
            'responses': {'200': {'description': 'The list of zip files available'}},
        }
    }
    _POST = {
        '/orders': {
            'summary': 'Request one order preparation',
            'parameters': [
                {
                    'name': 'parameters',
                    'in': 'body',
                    'schema': {'$ref': '#/definitions/SeadataPost'},
                }
            ],
            'responses': {'200': {'description': 'Asynchronous request launched'}},
        }
    }
    _PUT = {
        '/orders/<string:order_id>': {
            'summary': 'Request a link to download an order (if already prepared)',
            'responses': {
                '200': {
                    'description': 'The link to download the order (expires in 2 days)'
                }
            },
        }
    }
    _DELETE = {
        '/orders': {
            'summary': 'Remove one or more orders',
            'responses': {
                '200': {'description': 'Async job submitted for orders removal'}
            },
        }
    }

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required()
    def get(self, order_id):
        """ listing, not downloading """

        log.debug('GET request on orders')
        msg = prepare_message(self, json=None, log_string='start')
        log_into_queue(self, msg)

        ##################
        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            order_path = self.get_irods_order_path(imain, order_id)
            log.debug("Order path: {}", order_path)
            if not imain.is_collection(order_path):
                error = "Order '{}': not existing".format(order_id)
                return self.send_errors(error, code=404)

            ##################
            ils = imain.list(order_path, detailed=True)

            u = get_order_zip_file_name(order_id, restricted=False, index=1)
            # if a splitted unrestricted zip exists, skip the unsplitted file
            if u in ils:
                u = get_order_zip_file_name(order_id, restricted=False, index=None)
                ils.pop(u, None)

            r = get_order_zip_file_name(order_id, restricted=True, index=1)
            # if a splitted restricted zip exists, skip the unsplitted file
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
                response.append(data)

            msg = prepare_message(self, log_string='end', status='completed')
            log_into_queue(self, msg)
            return self.response(response)
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=503
            )

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required()
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
            error = "'{}' missing".format(main_key)
            return self.send_errors(error, code=400)

        ##################
        key = 'order_number'
        order_id = params.get(key)
        if order_id is None:
            error = "Order ID '{}': missing".format(key)
            return self.send_errors(error, code=400)
        else:
            order_id = str(order_id)

        # ##################
        # Get filename from json input. But it has to follow a
        # specific pattern, so we ignore client input if it does not...
        filename = "order_{}_unrestricted".format(order_id)
        key = 'file_name'
        if key in params and not params[key] == filename:
            log.warning(
                'Client provided wrong filename ({}), will use: {}',
                params[key],
                filename,
            )
        params[key] = filename

        ##################
        # PIDS: can be empty if restricted
        key = 'pids'
        pids = params.get(key, [])

        ##################
        # Create the path
        log.info("Order request: {}", order_id)
        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            order_path = self.get_irods_order_path(imain, order_id)
            log.debug("Order path: {}", order_path)
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
                return self.response(json_input)

            ################
            # ASYNC
            if len(pids) > 0:
                log.info("Submit async celery task")
                task = CeleryExt.unrestricted_order.apply_async(
                    args=[order_id, order_path, zip_file_name, json_input]
                )
                log.info("Async job: {}", task.id)
                return self.return_async_id(task.id)

            return self.response({'status': 'enabled'})
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=503
            )

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
        log.info("Ticket: {} -> {}", ticket, encoded)
        return encoded

    def get_download(
        self, imain, order_id, order_path, files, restricted=False, index=None
    ):

        zip_file_name = get_order_zip_file_name(order_id, restricted, index)

        if zip_file_name not in files:
            return None

        zip_ipath = path.join(order_path, zip_file_name, return_str=True)
        log.debug("Zip irods path: {}", zip_ipath)

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

        route = '{}{}/{}/{}/download/{}/c/{}'.format(
            CURRENT_HTTPAPI_SERVER,
            API_URL,
            ORDERS_ENDPOINT,
            order_id,
            ftype,
            code,
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
            'size': info.get('content_length', 0),
        }

    @decorators.catch_errors(exception=IrodsException)
    @decorators.auth.required()
    def put(self, order_id):

        log.info("Order request: {}", order_id)
        msg = prepare_message(self, json={'order_id': order_id}, log_string='start')
        log_into_queue(self, msg)

        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            try:
                order_path = self.get_irods_order_path(imain, order_id)
                log.debug("Order path: {}", order_path)
            except BaseException:
                return self.send_errors(
                    "Order not found",
                    code=404
                )

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
                imain, order_id, order_path, files_in_irods, restricted=False, index=1
            )

            # No split zip found, looking for the single unrestricted zip
            if info is None:
                info = self.get_download(
                    imain,
                    order_id,
                    order_path,
                    files_in_irods,
                    restricted=False,
                    index=None,
                )
                if info is not None:
                    response.append(info)
            # When found one split, looking for more:
            else:
                response.append(info)
                for index in range(2, 100):
                    info = self.get_download(
                        imain,
                        order_id,
                        order_path,
                        files_in_irods,
                        restricted=False,
                        index=index,
                    )
                    if info is not None:
                        response.append(info)

            # checking for splitted restricted zip
            info = self.get_download(
                imain, order_id, order_path, files_in_irods, restricted=True, index=1
            )

            # No split zip found, looking for the single restricted zip
            if info is None:
                info = self.get_download(
                    imain, order_id, order_path, files_in_irods, restricted=True, index=None
                )
                if info is not None:
                    response.append(info)
            # When found one split, looking for more:
            else:
                response.append(info)
                for index in range(2, 100):
                    info = self.get_download(
                        imain,
                        order_id,
                        order_path,
                        files_in_irods,
                        restricted=True,
                        index=index,
                    )
                    if info is not None:
                        response.append(info)

            if len(response) == 0:
                error = "Order '{}' not found (or no permissions)".format(order_id)
                return self.send_errors(error, code=404)

            msg = prepare_message(self, log_string='end', status='enabled')
            log_into_queue(self, msg)

            return self.response(response)
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=503
            )
        except NetworkException as e:
            log.error(e)
            return self.send_errors(
                "Could not connect to B2SAFE host",
                code=503
            )

    @decorators.auth.required()
    def delete(self):

        json_input = self.get_input()

        # imain = self.get_service_instance(service_name='irods')
        try:
            imain = self.get_main_irods_connection()
            order_path = self.get_irods_order_path(imain)
            local_order_path = str(path.join(MOUNTPOINT, ORDERS_DIR))
            log.debug("Order collection: {}", order_path)
            log.debug("Order path: {}", local_order_path)

            task = CeleryExt.delete_orders.apply_async(
                args=[order_path, local_order_path, json_input]
            )
            log.info("Async job: {}", task.id)
            return self.return_async_id(task.id)
        except requests.exceptions.ReadTimeout:
            return self.send_errors(
                "B2SAFE is temporarily unavailable",
                code=503
            )
