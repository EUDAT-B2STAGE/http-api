from restapi.customizer import BaseCustomizer
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

        # or return something else, maybe an empty dict if extra fields are not editable
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
