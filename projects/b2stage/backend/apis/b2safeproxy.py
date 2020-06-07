from b2stage.apis.commons.b2access import B2accessUtilities
from flask_apispec import MethodResource, use_kwargs
from marshmallow import fields
from restapi import decorators
from restapi.connectors.irods.client import IrodsException, iexceptions
from restapi.exceptions import RestApiException
from restapi.models import InputSchema
from restapi.utilities.logs import log


class Credentials(InputSchema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, password=True,)
    authscheme = fields.Str(default="credentials")


class B2safeProxy(MethodResource, B2accessUtilities):
    """ Login to B2SAFE: directly. """

    _anonymous_user = "anonymous"

    baseuri = "/auth"
    labels = ["eudat", "b2safe", "authentication"]
    _GET = {
        "/b2safeproxy": {
            "summary": "Test a token obtained as a B2SAFE user",
            "responses": {"200": {"description": "token is valid"}},
        }
    }
    _POST = {
        "/b2safeproxy": {
            "summary": "Authenticate inside HTTP API with B2SAFE user",
            "description": "Normal credentials (username and password) login endpoint",
            "responses": {
                "401": {
                    "description": "Invalid username or password for the current B2SAFE instance"
                },
                "200": {"description": "B2SAFE credentials provided are valid"},
            },
        }
    }

    def get_and_verify_irods_session(self, parameters):

        obj = None
        username = parameters.get("user")

        try:
            obj = self.get_service_instance(**parameters)

        except iexceptions.CAT_INVALID_USER:
            log.warning("Invalid user: {}", username)
        except iexceptions.UserDoesNotExist:
            log.warning("Invalid iCAT user: {}", username)
        except iexceptions.CAT_INVALID_AUTHENTICATION:
            log.warning("Invalid password for {}", username)
        except BaseException as e:
            log.warning('Failed with unknown reason:\n[{}] "{}"', type(e), e)
            error = "Failed to verify credentials against B2SAFE. " + "Unknown error: "
            if str(e).strip() == "":
                error += e.__class__.__name__
            else:
                error += str(e)
            raise IrodsException(error)

        return obj

    @decorators.catch_errors()
    @decorators.auth.required()
    def get(self):

        user = self.auth.get_user()
        log.debug("Token user: {}", user)

        if user.session is not None and len(user.session) > 0:
            log.info("Valid B2SAFE user: {}", user.uuid)
        else:
            msg = "This user is not registered inside B2SAFE"
            raise RestApiException(msg, status_code=401)

        icom = self.get_service_instance(service_name="irods", user_session=user)
        icom.list()
        return "validated"

    @decorators.catch_errors()
    @use_kwargs(Credentials)
    def post(self, username, password, authscheme="credentials"):

        # # token is an alias for password parmeter
        # if password is None:
        #     password = jargs.pop('token', None)

        if authscheme.upper() == "PAM":
            authscheme = "PAM"

        if username == self._anonymous_user:
            password = "WHATEVERYOUWANT:)"

        if not username or not password:
            raise RestApiException("Missing username or password", status_code=401)

        if authscheme.upper() == "OPENID":
            authscheme = "PAM"
            imain = self.get_main_irods_connection()

            username = self.get_irods_user_from_b2access(imain, username)

        #############
        params = {
            "service_name": "irods",
            "user": username,
            "password": password,
            "authscheme": authscheme,
        }

        # we verify that irods connects with this credentials
        irods = self.get_and_verify_irods_session(params)
        if irods is None:
            msg = "Failed to authenticate on B2SAFE"
            raise RestApiException(msg, status_code=401)
        else:
            encoded_session = irods.prc.serialize()

        token, irods_user = self.irods_user(username, encoded_session)

        #############
        response = {"token": token}
        imain = self.get_service_instance(service_name="irods")

        user_home = imain.get_user_home(irods_user)
        if imain.is_collection(user_home):
            response["b2safe_home"] = user_home
        else:
            response["b2safe_home"] = imain.get_user_home(append_user=False)

        response["b2safe_user"] = irods_user

        return self.response(response)
