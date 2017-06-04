# -*- coding: utf-8 -*-

from rapydo.rest.definition import EndpointResource
from rapydo import decorators as decorate
from rapydo.utils.logs import get_logger
from rapydo.flask_ext.flask_irods.client import IrodsException
log = get_logger(__name__)


class RPC(EndpointResource):

    @decorate.catch_error(exception=IrodsException, catch_generic=False)
    def get(self, irods_location=None):

        icom = self.get_service_instance('rpc')

        # from irods.models import User
        # results = icom.rpc.query(User.name).all()
        home = "/%s/home/%s" % (icom.rpc.zone, icom.rpc.username)
        print("IRODS", icom.rpc, home)

        from b2handle.searcher import Searcher
        print("TEST B2HANDLE", Searcher)

        dirname = home + "/pippo"
        # dirname2 = home + "/clarabella"
        filename = home + "/pippo/pluto.txt"
        filename2 = home + "/pippo/topolino.txt"
        # filename3 = home + "/pippo/paperino.txt"

        icom.create_empty(dirname, directory=True, ignore_existing=True)
        icom.create_empty(filename, directory=False, ignore_existing=True)

        icom.set_inheritance(dirname, inheritance=True, recursive=False)
        icom.set_permissions(dirname, "read", "guest", recursive=True)
        icom.set_permissions(filename, "write", "guest", recursive=False)

        icom.copy(filename, filename2, recursive=False, force=True)
        # icom.copy(dirname, dirname2, recursive=True, force=False)

        # icom.move(filename2, filename3)

        icom.write_file_content(filename, "pippo pluto e topolino\nE Orazio?")
        icom.open(filename, "/tmp/mytext.txt")
        icom.save("/tmp/mytext.txt", home + "/prova.txt", force=True)

        out = icom.get_file_content(home + "/prova.txt")

        out = icom.list(path=home, recursive=True, detailed=True, acl=True)

        out = icom.get_user_info("guest")
        out = str(icom.user_has_group("guest", "public2"))
        _, out = icom.check_user_exists("guest", "public2")

        meta = {'PID': '/123/45678901', 'EUDAT/CHECKSUM': 'md5md5md5md5md5'}
        icom.set_metadata(filename, **meta)
        out, _ = icom.get_metadata(filename)
        # print(out.get("PID"))
        icom.remove(filename)
        icom.remove(dirname, recursive=True)

        # return "Hello"
        return out
