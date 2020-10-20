import os

from restapi.customizer import BaseCustomizer
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
                            user.roles.append(sql.Role.query.filter_by(name=r).first())
                        sql.session.add(user)
                        sql.session.commit()
                        log.info("User {} created with roles: {}", username, roles)
                    except BaseException as e:
                        log.error("Errors creating user {}: {}", username, str(e))


class Customizer(BaseCustomizer):
    @staticmethod
    def custom_user_properties_pre(properties):
        extra_properties = {}
        # if 'myfield' in properties:
        #     extra_properties['myfield'] = properties['myfield']
        return properties, extra_properties

    @staticmethod
    def custom_user_properties_post(user, properties, extra_properties, db):
        pass

    @staticmethod
    def manipulate_profile(ref, user, data):
        # data['CustomField'] = user.custom_field

        return data

    @staticmethod
    def get_user_editable_fields(request):

        return {}

    @staticmethod
    def get_custom_input_fields(request):

        # required = request and request.method == "POST"
        """
        return {
            'custom_field': fields.Int(
                required=required,
                # validate=validate.Range(min=0, max=???),
                validate=validate.Range(min=0),
                label="CustomField",
                description="This is a custom field"
            )
        }
        """
        return {}

    @staticmethod
    def get_custom_output_fields(request):
        return Customizer.get_custom_input_fields(request)
