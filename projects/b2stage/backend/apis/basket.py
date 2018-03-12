# -*- coding: utf-8 -*-

"""
Orders from production data to be temporary downloadable with a zip file

PUT /api/order/<OID>/add/<PID>
PUT /api/order/<OID>/download/prepare
PUT /api/order/<OID>/download/link
"""

#################
# IMPORTS
# from restapi.rest.definition import EndpointResource
# from b2stage.apis.commons.cluster import ClusterContainerEndpoint
# from b2stage.apis.commons.b2handle import B2HandleEndpoint
from b2stage.apis.commons.endpoint import EudatEndpoint
# from b2stage.apis.commons.seadatacloud import Metadata as md
# from utilities import htmlcodes as hcodes
# from restapi import decorators as decorate
# from restapi.flask_ext.flask_irods.client import IrodsException
from utilities.logs import get_logger

#################
# INIT VARIABLES
log = get_logger(__name__)


#################
# REST CLASS
# class Basket(B2HandleEndpoint, ClusterContainerEndpoint):
class Basket(EudatEndpoint):

    def get(self, order_id):

        log.info("Order request: %s", order_id)

        # ###################
        # # Init EUDAT endpoint resources
        # r = self.init_endpoint()
        # if r.errors is not None:
        #     return self.send_errors(errors=r.errors)
        # icom = r.icommands
        # # imain = self.get_service_instance(service_name='irods')

        ###################
        # Add a file from production to order directory

        # ##################
        # order_path = self.get_order_path(imain, order_id)
        # log.debug("Order path: %s", order_path)

        # ##################
        # # ITICKET
        # ipath = '/tempZone/home/paolobeta/test.txt'
        # ticket = icom.ticket(ipath)
        # # save to db?
        # print("TICKET", ticket.ticket)

        # ##################
        response = 'Hello world!'
        return self.force_response(response)
