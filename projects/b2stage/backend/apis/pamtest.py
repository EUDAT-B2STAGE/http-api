# -*- coding: utf-8 -*-


from b2stage.apis.commons.cluster import ClusterContainerEndpoint as Endpoint
from utilities.logs import get_logger

log = get_logger(__name__)


class PAMTest(Endpoint):

    def post(self):

        imain = self.get_service_instance(service_name='irods')
        out = imain.list()
        return out
