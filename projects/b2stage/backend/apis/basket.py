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
from utilities import htmlcodes as hcodes
# from restapi import decorators as decorate
# from restapi.flask_ext.flask_irods.client import IrodsException
from utilities.logs import get_logger

#################
# INIT VARIABLES
log = get_logger(__name__)


#################
# REST CLASS
# class BasketEndpoint(EudatEndpoint):
class BasketEndpoint(B2HandleEndpoint, ClusterContainerEndpoint):

    def get(self, order_id):

        ##################
        log.debug('GET request on orders')
        parameters = self.get_input()

        ##################
        key = 'code'
        code = parameters.get(key)
        if code is None:
            error = "Parameter '%s' is missing" % key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        log.info("Order request: %s (code '%s')", order_id, code)

        ##################
        response = 'Hello world!'
        return self.force_response(response)

    def post(self):

        ##################
        log.debug('POST request on orders')
        json_input = self.get_input()

        ##################
        key = 'order_id'
        order_id = json_input.get(key)
        if order_id is None:
            error = "Parameter '%s' is missing" % key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        key = 'pids'
        pids = json_input.get(key)
        if pids is None:
            error = "Parameter '%s' is missing" % key
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)
        if not isinstance(pids, list) or len(pids) < 1:
            error = "Parameter '%s' " % key + \
                "must be a list (with at least one element)"
            return self.send_errors(error, code=hcodes.HTTP_BAD_REQUEST)

        ##################
        log.info("Order request: %s", order_id)
        imain = self.get_service_instance(service_name='irods')
        order_path = self.get_order_path(imain, order_id)
        log.debug("Order path: %s", order_path)
        log.debug("PID list: %s", pids)

        ##################
        # Create the path

        ##################
        # Add all file from production to order directory
        # @async!

        ##################
        response = 'Hello world!'
        return self.force_response(response)

    def put(self, order_id):

        log.info("Order request: %s", order_id)

        # ###################
        # # Init EUDAT endpoint resources
        # r = self.init_endpoint()
        # if r.errors is not None:
        #     return self.send_errors(errors=r.errors)
        # icom = r.icommands
        imain = self.get_service_instance(service_name='irods')

        ##################
        order_path = self.get_order_path(imain, order_id)
        log.debug("Order path: %s", order_path)

        ##################
        # verify if the path exists

        # ##################
        # # ITICKET
        # ipath = '/tempZone/home/paolobeta/test.txt'
        # ticket = icom.ticket(ipath)
        # # save to db?
        # print("TICKET", ticket.ticket)

        # TODO: investigate iticket expiration
        # iticket mod Ticket_string-or-id uses/expire string-or-none

        ##################
        response = 'Hello world!'
        return self.force_response(response)

    def delete(self, order_id):

        ##################
        log.debug('DELETE request on orders')
        log.info("Order request: %s", order_id)

        ##################
        # verify if the path exists

        ##################
        # remove the iticket

        ##################
        # remove the path

        ##################
        response = 'Hello world!'
        return self.force_response(response)
