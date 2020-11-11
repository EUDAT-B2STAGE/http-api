from b2stage.connectors import irods
from b2stage.connectors.irods.client import IrodsException, iexceptions
from b2stage.endpoints.commons.b2access import B2accessUtilities
from restapi import decorators
from restapi.exceptions import Unauthorized
from restapi.models import Schema, fields
from restapi.utilities.logs import log


class Credentials(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, password=True,)
    authscheme = fields.Str(default="credentials")


class B2safeProxy(B2accessUtilities):
    """ Login to B2SAFE: directly. """

    _anonymous_user = "anonymous"

    baseuri = "/auth"
    labels = ["eudat", "b2safe", "authentication"]

    def get_and_verify_irods_session(self, user, password, authscheme):

        obj = None

        try:
            obj = irods.get_instance(
                user=user, password=password, authscheme=authscheme,
            )

        except iexceptions.CAT_INVALID_USER:
            log.warning("Invalid user: {}", user)
        except iexceptions.UserDoesNotExist:
            log.warning("Invalid iCAT user: {}", user)
        except iexceptions.CAT_INVALID_AUTHENTICATION:
            log.warning("Invalid password for {}", user)
        except BaseException as e:
            log.warning('Failed with unknown reason:\n[{}] "{}"', type(e), e)
            error = "Failed to verify credentials against B2SAFE. " + "Unknown error: "
            if str(e).strip() == "":
                error += e.__class__.__name__
            else:
                error += str(e)
            raise IrodsException(error)

        return obj

    @decorators.auth.require()
    @decorators.endpoint(
        path="/b2safeproxy",
        summary="Test a token obtained as a b2safe user",
        responses={200: "Token is valid"},
    )
    def get(self):

        user = self.get_user()
        log.debug("Token user: {}", user)

        if user.session is not None and len(user.session) > 0:
            log.info("Valid B2SAFE user: {}", user.uuid)
        else:
            raise Unauthorized("This user is not registered inside B2SAFE")

        icom = self.get_service_instance(service_name="irods", user_session=user)
        icom.list()
        return "validated"

    @decorators.use_kwargs(Credentials)
    @decorators.endpoint(
        path="/b2safeproxy",
        summary="Authenticate inside http api with b2safe user",
        description="Normal credentials (username and password) login endpoint",
        responses={
            401: "Invalid username or password for the current b2safe instance",
            200: "B2safe credentials provided are valid",
        },
    )
    def post(self, username, password, authscheme="credentials"):

        # # token is an alias for password parmeter
        # if password is None:
        #     password = jargs.pop('token', None)

        if authscheme.upper() == "PAM":
            authscheme = "PAM"

        if username == self._anonymous_user:
            password = "WHATEVERYOUWANT:)"

        if not username or not password:
            raise Unauthorized("Missing username or password")

        if authscheme.upper() == "OPENID":
            authscheme = "PAM"
            imain = self.get_main_irods_connection()

            username = self.get_irods_user_from_b2access(imain, username)

        # we verify that irods connects with this credentials
        irods = self.get_and_verify_irods_session(
            user=username, password=password, authscheme=authscheme,
        )
        if irods is None:
            raise Unauthorized("Failed to authenticate on B2SAFE")

        encoded_session = irods.prc.serialize()
        token, irods_user = self.irods_user(username, encoded_session)

        response = {"token": token}
        imain = self.get_service_instance(service_name="irods")

        user_home = imain.get_user_home(irods_user)
        if imain.is_collection(user_home):
            response["b2safe_home"] = user_home
        else:
            response["b2safe_home"] = imain.get_user_home(append_user=False)

        response["b2safe_user"] = irods_user

        return self.response(response)
