import os

from restapi.services.authentication import Role
from restapi.utilities.logs import log
from restapi.utilities.uuid import getUUID


class Initializer:
    def __init__(self, services, app=None):

        sql = services.get("sqlalchemy", None)

        if sql is None:
            log.critical("Unable to retrieve sqlalchemy service")
            return

        if app is None:
            log.critical("Unable to retrieve app context")
            return

        with app.app_context():
            users = os.getenv("SEADATA_PRIVILEGED_USERS")

            if users is None or users == "":
                users = []
            else:
                users = users.replace(" ", "").split(",")
            roles = [Role.USER, Role.STAFF]
            if len(users) == 0:
                log.info("No privileged user found")
            else:
                for username in users:

                    if username == "":
                        log.warning("Invalid username: [{}]", username)
                        continue
                    try:
                        log.info("Creating user {}", username)
                        userdata = {
                            "uuid": getUUID(),
                            "email": username,
                            "name": username,
                            "surname": "iCAT",
                            "authmethod": "irods",
                        }
                        user = sql.User(**userdata)
                        for r in roles:
                            role = sql.Role.query.filter_by(name=r.value).first()
                            user.roles.append(role)
                        sql.session.add(user)
                        sql.session.commit()
                        log.info("User {} created with roles: {}", username, roles)
                    except BaseException as e:
                        log.error("Errors creating user {}: {}", username, str(e))
