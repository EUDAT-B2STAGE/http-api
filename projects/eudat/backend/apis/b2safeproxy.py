# -*- coding: utf-8 -*-

"""
Login to B2SAFE directly
"""

from restapi import decorators as decorate
from restapi.rest.definition import EndpointResource
from restapi.exceptions import RestApiException
from restapi.flask_ext.flask_irods.client import get_and_verify_irods_session
from restapi.services.detect import detector
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


class B2safeProxy(EndpointResource):

    @decorate.catch_error()
    def get(self):
        response = 'Hello world!'

        #############
        user = self.auth.get_user()
        if user.session is not None and len(user.session) > 0:
            log.debug("Valid B2SAFE user: %s" % user.uuid)
        else:
            raise ValueError("This user is not registered inside B2SAFE")

        icom = self.get_service_instance(
            service_name='irods',
            user_session=user,
        )
        print("Working with", icom)

        #############
        return self.force_response(response)

    @decorate.catch_error()
    def post(self):

        #############
        jargs = self.get_input()
        username = jargs.get('username')
        password = jargs.get('password')

        if username is None or password is None:
            msg = "Missing username or password"
            raise RestApiException(
                msg, status_code=hcodes.HTTP_BAD_UNAUTHORIZED)

        # #############
        # security = HandleSecurity(self.auth)
        # security.verify_blocked_username(username)

        #############
        func = self.get_service_instance
        params = {
            'service_name': "irods",
            'user': username,
            'password': password,
        }
        # we verify that irods connects with this credentials
        irods = get_and_verify_irods_session(func, params)
        if irods is None:
            raise AttributeError("Failed to authenticate on B2SAFE")
        else:
            encoded_session = irods.rpc.serialize()

        token = self.auth.irods_user(username, encoded_session)
        return {'token': token}
