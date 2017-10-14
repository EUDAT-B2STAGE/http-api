# -*- coding: utf-8 -*-

from restapi import decorators as decorate
from restapi.rest.definition import EndpointResource
from restapi.exceptions import RestApiException
from restapi.flask_ext.flask_irods.client import get_and_verify_irods_session
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


class B2safeProxy(EndpointResource):
    """ Login to B2SAFE: directly. """

    anonymous_user = 'anonymous'

    @decorate.catch_error()
    def get(self):

        user = self.get_current_user()
        log.debug("Token user: %s" % user)

        if user.session is not None and len(user.session) > 0:
            log.info("Valid B2SAFE user: %s" % user.uuid)
        else:
            msg = "This user is not registered inside B2SAFE"
            raise RestApiException(
                msg, status_code=hcodes.HTTP_BAD_UNAUTHORIZED)

        icom = self.get_service_instance(
            service_name='irods',
            user_session=user,
        )
        icom.list()
        return 'validated'

    @decorate.catch_error()
    def post(self):

        #############
        from flask import request
        auth = request.authorization

        if auth is not None:
            username = auth.username
            password = auth.password
        else:
            jargs = self.get_input()
            username = jargs.get('username')
            password = jargs.get('password')

        if username == self.anonymous_user:
            password = 'WHATEVERYOUWANT:)'

        if username is None or password is None or \
           username.strip() == '' or password.strip() == '':
            msg = "Missing username or password"
            raise RestApiException(
                msg, status_code=hcodes.HTTP_BAD_UNAUTHORIZED)

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
            msg = "Failed to authenticate on B2SAFE"
            raise RestApiException(
                msg, status_code=hcodes.HTTP_BAD_UNAUTHORIZED)
        else:
            encoded_session = irods.prc.serialize()

        token, irods_user = self.auth.irods_user(username, encoded_session)

        # Get the default irods user just to compute current user home
        ihandle = self.get_service_instance(service_name='irods')
        user_home = ihandle.get_user_home(irods_user)

        #############
        return self.force_response(
            defined_content={
                'token': token,
                'b2safe_user': irods_user,
                'b2safe_home': user_home,
            }
        )
