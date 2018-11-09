# -*- coding: utf-8 -*-
import os
from utilities.logs import get_logger

log = get_logger(__name__)


class Initializer(object):

    def __init__(self, services):

        log.critical(os.environ)
        log.critical(services)
        # # create user
        # user = self.db.User(
        #     email=username, name=username, surname='iCAT',
        #     uuid=getUUID(), authmethod='irods', session=session,
        # )
        # # add role
        # user.roles.append(
        #     self.db.Role.query.filter_by(name=self.default_role).first())
