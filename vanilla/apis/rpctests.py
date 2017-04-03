# -*- coding: utf-8 -*-

from rapydo.rest.definition import EndpointResource
from rapydo.utils.logs import get_logger
log = get_logger(__name__)


class RPC(EndpointResource):

    def get(self, irods_location=None):

        # from irods.models import User
        # results = self.rpc.query(User.name).all()
        # log.pp(self.rpc)
        print("IRODS", self.rpc)
        home = "/%s/home/%s" % (self.rpc.zone, self.rpc.username)
        coll = self.rpc.collections.get(home)
        print(coll)
        return "Hello"
