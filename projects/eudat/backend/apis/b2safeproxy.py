# -*- coding: utf-8 -*-

"""
Login to B2SAFE directly
"""

from restapi.rest.definition import EndpointResource
from restapi.exceptions import RestApiException
from restapi.flask_ext.flask_irods.client import get_and_verify_irods_session
from restapi import decorators as decorate
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


class B2safeProxy(EndpointResource):

    @decorate.catch_error()
    def post(self):
        response = 'Hello world!'
        jargs = self.get_input()
        username = jargs.get('username')
        password = jargs.get('password')

        #############
        if username is None or password is None:
            msg = "Missing username or password"
            raise RestApiException(
                msg, status_code=hcodes.HTTP_BAD_UNAUTHORIZED)

        #############
        sql = self.get_service_instance('sqlalchemy')
        func = self.get_service_instance
        params = {
            'service_name': "irods",
            'user': username,
            'password': password,
        }
        irods = get_and_verify_irods_session(func, params)
        if irods is None:
            print("FAILED")
        else:
            print("TEST", sql, irods)

        #############
        return self.force_response(response)
