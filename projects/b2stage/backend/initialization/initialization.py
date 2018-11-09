# -*- coding: utf-8 -*-
import os

from utilities.uuid import getUUID
from utilities.logs import get_logger

log = get_logger(__name__)


class Initializer(object):

    def __init__(self, services):

        sql = services.get('sqlalchemy', None)

        if sql is None:
            log.critical("Unable to retrieve sqlalchemy service")
            return

        if os.environ.get('SEADATA_PROJECT', False):

            for username in ['stresstest']:
                log.info("Creating user %s", username)
                userdata = {
                    "uuid": getUUID(),
                    "email": username,
                    "name": username,
                    "surname": 'iCAT',
                    "authmethod": 'irods',
                }
                user = sql.User(**userdata)
                for r in ['normal_user', 'staff_user']:
                    user.roles.append(
                        sql.Role.query.filter_by(name=r).first())
                sql.session.add(user)
                sql.session.commit()
