# -*- coding: utf-8 -*-

from restapi import decorators
from b2stage.apis.commons.b2access import B2accessUtilities
from restapi.exceptions import RestApiException
from restapi.connectors.irods.client import get_and_verify_irods_session
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class B2safeProxy(B2accessUtilities):
    """ Login to B2SAFE: directly. """

    _anonymous_user = 'anonymous'

    baseuri = '/auth'
    labels = ['eudat', 'b2safe', 'authentication']
    GET = {
        '/b2safeproxy': {
            'summary': 'Test a token obtained as a B2SAFE user',
            'responses': {'200': {'description': 'token is valid'}},
        }
    }
    POST = {
        '/b2safeproxy': {
            'summary': 'Authenticate inside HTTP API with B2SAFE user',
            'description': 'Normal credentials (username and password) login endpoint',
            'parameters': [
                {
                    'name': 'b2safe_credentials',
                    'in': 'body',
                    'schema': {'$ref': '#/definitions/Credentials'},
                }
            ],
            'responses': {
                '401': {
                    'description': 'Invalid username or password for the current B2SAFE instance'
                },
                '200': {'description': 'B2SAFE credentials provided are valid'},
            },
        }
    }

    @decorators.catch_errors()
    @decorators.auth.required()
    def get(self):

        user = self.auth.get_user()
        log.debug("Token user: {}", user)

        if user.session is not None and len(user.session) > 0:
            log.info("Valid B2SAFE user: {}", user.uuid)
        else:
            msg = "This user is not registered inside B2SAFE"
            raise RestApiException(msg, status_code=hcodes.HTTP_BAD_UNAUTHORIZED)

        icom = self.get_service_instance(service_name='irods', user_session=user)
        icom.list()
        return 'validated'

    @decorators.catch_errors()
    def post(self):

        #############
        from flask import request

        auth = request.authorization

        jargs = self.get_input()
        if auth is not None:
            username = auth.username
            password = auth.password
        else:
            username = jargs.pop('username', None)
            password = jargs.pop('password', None)
        authscheme = jargs.pop('authscheme', 'credentials')

        # token is an alias for password parmeter
        if password is None:
            password = jargs.pop('token', None)

        if len(jargs) > 0:
            for j in jargs:
                log.warning("Unknown input parameter: {}", j)

        if authscheme.upper() == 'PAM':
            authscheme = 'PAM'

        if username == self._anonymous_user:
            password = 'WHATEVERYOUWANT:)'

        if (
            username is None
            or password is None
            or username.strip() == ''
            or password.strip() == ''
        ):
            msg = "Missing username or password"
            raise RestApiException(msg, status_code=hcodes.HTTP_BAD_UNAUTHORIZED)

        if authscheme.upper() == 'OPENID':
            authscheme = 'PAM'
            imain = self.get_main_irods_connection()

            username = self.get_irods_user_from_b2access(imain, username)

        #############
        func = self.get_service_instance
        params = {
            'service_name': "irods",
            'user': username,
            'password': password,
            'authscheme': authscheme,
        }

        # we verify that irods connects with this credentials
        irods = get_and_verify_irods_session(func, params)
        if irods is None:
            msg = "Failed to authenticate on B2SAFE"
            raise RestApiException(msg, status_code=hcodes.HTTP_BAD_UNAUTHORIZED)
        else:
            encoded_session = irods.prc.serialize()

        token, irods_user = self.auth.irods_user(username, encoded_session)

        #############
        response = {'token': token}
        imain = self.get_service_instance(service_name='irods')

        user_home = imain.get_user_home(irods_user)
        if imain.is_collection(user_home):
            response['b2safe_home'] = user_home
        else:
            response['b2safe_home'] = imain.get_user_home(append_user=False)

        response['b2safe_user'] = irods_user

        return self.response(response)
