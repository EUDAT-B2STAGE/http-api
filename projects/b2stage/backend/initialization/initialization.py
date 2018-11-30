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
                users = os.environ.get('SEADATA_PRIVILEGED_USERS')

                if users is None or users == "":
                    users = []
                else:
                    users = users.replace(' ', '').split(',')
                # users = ['stresstest', 'svanderhorst']
                roles = ['normal_user', 'staff_user']
                if len(users) == 0:
                    log.info("No privileged user found")
                else:
                    for username in users:

                        if username == "":
                            log.warning("Invalid username: [%s]", username)
                            continue
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
                                user.roles.append(
                                    sql.Role.query.filter_by(name=r).first())
                            sql.session.add(user)
                            sql.session.commit()
                            log.info("User %s created with roles: %s", username, roles)
                        except BaseException as e:
                            log.error("Errors creating user %s: %s", username, str(e))
