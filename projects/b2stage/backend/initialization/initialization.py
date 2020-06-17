import os

from restapi.utilities.logs import log


class Initializer:
    def __init__(self, services, app=None):

        sql = services.get("sqlalchemy", None)

        if sql is None:
            log.critical("Unable to retrieve sqlalchemy service")
            return

        if app is None:
            log.critical("Unable to retrieve app context")
            return


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
