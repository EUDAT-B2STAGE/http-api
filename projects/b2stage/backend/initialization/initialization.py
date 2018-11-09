# -*- coding: utf-8 -*-
import os

from utilities.uuid import getUUID
from utilities.logs import get_logger

log = get_logger(__name__)


class Initializer(object):

    def __init__(self, services, app=None):

        sql = services.get('sqlalchemy', None)

        if sql is None:
            log.critical("Unable to retrieve sqlalchemy service")
            return

        if app is None:
            log.critical("Unable to retrieve app context")
            return

        if os.environ.get('SEADATA_PROJECT', False):

            with app.app_context():
                users = ['stresstest', 'svanderhorst']
                roles = ['normal_user', 'staff_user']
                for username in users:
                    try:
                        log.info("Creating user %s", username)
                        userdata = {
                            "uuid": getUUID(),
                            "email": username,
                            "name": username,
                            "surname": 'iCAT',
                            "authmethod": 'irods',
                        }
                        user = sql.User(**userdata)
                        for r in roles:
                            log.info("Retrieving role %s", r)
                            user.roles.append(
                                sql.Role.query.filter_by(name=r).first())
                        sql.session.add(user)
                        sql.session.commit()
                        log.info("User %s created with roles: %s", username, roles)
                    except BaseException as e:
                        log.error("Errors creating user %s: %s", username, str(e))
