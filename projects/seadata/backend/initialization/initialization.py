import os

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
            # users = ['stresstest', 'svanderhorst']
            roles = ["normal_user", "staff_user"]
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
                            user.roles.append(sql.Role.query.filter_by(name=r).first())
                        sql.session.add(user)
                        sql.session.commit()
                        log.info("User {} created with roles: {}", username, roles)
                    except BaseException as e:
                        log.error("Errors creating user {}: {}", username, str(e))


class Customizer:
    """
    This class is used to manipulate user information
    - custom_user_properties is executed just before user creation
                             use this to removed or manipulate input properties
                             before sending to the database
    - custom_post_handle_user_input is used just after user registration
                                    use this to perform setup operations,
                                    such as verify default settings
    """

    def custom_user_properties(self, properties):
        return properties

    def custom_post_handle_user_input(self, auth, user_node, properties):

        return True
