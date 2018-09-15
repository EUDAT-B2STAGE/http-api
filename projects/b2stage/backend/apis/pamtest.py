# -*- coding: utf-8 -*-

from b2stage.apis.commons.cluster import ClusterContainerEndpoint as Endpoint
from utilities.logs import get_logger

log = get_logger(__name__)


class PAMTest(Endpoint):

    def post(self):

        jargs = self.get_input()
        user = jargs.get('username')
        password = jargs.get('password')

        log.info("Received user: %s", user)
        log.debug("Authenticating to b2safe...")
        imain = self.get_service_instance(
            service_name='irods',
            user=user,
            password=password
        )
        log.debug("B2safe authenticated")
        out = imain.list()
        log.info(out)
        return out
