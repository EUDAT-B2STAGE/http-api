# -*- coding: utf-8 -*-

from b2stage.apis.commons.cluster import ClusterContainerEndpoint as Endpoint
from restapi.exceptions import RestApiException
from restapi import decorators as decorate
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


class PAMTest(Endpoint):

    @decorate.catch_error()
    def post(self):

        jargs = self.get_input()
        user = jargs.get('username')
        password = jargs.get('password')

        if user is None:
            raise RestApiException(
                'User cannot be empty',
                status_code=hcodes.HTTP_BAD_REQUEST
            )

        if password is None:
            raise RestApiException(
                'Password cannot be empty',
                status_code=hcodes.HTTP_BAD_REQUEST
            )

        log.info("Received user: %s", user)
        log.debug("Authenticating to b2safe...")
        imain = self.get_service_instance(
            service_name='irods',
            user=user,
            password=password,
            authscheme='PAM',
            catch_exceptions=True
        )
        u = imain.get_current_user()
        log.debug("B2safe authenticated with user = %s", u)

        info = imain.get_user_info(u)
        out = imain.list()
        return {"user": info, "home": out}
