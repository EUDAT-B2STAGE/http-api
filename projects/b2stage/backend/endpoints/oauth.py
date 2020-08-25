"""
OAUTH2 authentication with EUDAT services
"""

from b2stage.endpoints.commons import PRODUCTION
from b2stage.endpoints.commons.endpoint import EudatEndpoint
from flask import request, url_for
from restapi import decorators
from restapi.exceptions import RestApiException, ServiceUnavailable
from restapi.utilities.logs import log


class OauthLogin(EudatEndpoint):
    """
    Endpoint which redirects to B2ACCESS server online,
    to ask the current user for authorization/token.
    """

    baseuri = "/auth"
    labels = ["eudat", "b2access", "authentication"]
    depends_on = ["B2ACCESS_APPKEY"]

    @decorators.endpoint(
        path="/askauth",
        summary="Redirection to b2access oauth2 login",
        responses={200: "Redirected"},
    )
    def get(self):

        if request.user_agent.browser is None:
            raise RestApiException(
                "B2ACCESS authorization must be requested from a browser",
                status_code=405,
            )

        try:

            if not (b2access := self.create_b2access_client(self.auth)):
                raise RestApiException(
                    "B2ACCESS integration is not enabled", status_code=503
                )

            authorized_uri = url_for("authorize", _external=True)
            if PRODUCTION:
                # What needs a fix:
                # http://awesome.docker:443/auth/authorize
                # curl -i -k https://awesome.docker/auth/askauth
                authorized_uri = authorized_uri.replace("http:", "https:").replace(
                    ":443", ""
                )

            log.info("Ask redirection to: {}", authorized_uri)

            return b2access.authorize(callback=authorized_uri)
        except RuntimeError as e:
            raise ServiceUnavailable(str(e))


class Authorize(EudatEndpoint):
    """
    Previous endpoint will redirect here if authorization was granted.
    Use the B2ACCESS token to retrieve info about the user
    """

    baseuri = "/auth"
    labels = ["eudat", "b2access", "authentication"]
    depends_on = ["B2ACCESS_APPKEY"]

    @decorators.endpoint(
        path="/authorize",
        summary="Produce internal token if b2access authorization is granted",
        responses={200: "Rest api token from b2access authentication"},
    )
    def get(self):
        """
        Get the data for upcoming operations.

        Note: all of this actions are based on our user to have granted
        permissions to access his profile data.
        """

        # Get b2access token
        auth = self.auth
        b2access = self.create_b2access_client(auth, decorate=True)
        (
            b2access_token,
            b2access_refresh_token,
            b2access_error,
        ) = self.request_b2access_token(b2access)
        if b2access_token is None:
            return self.send_errors(errors=b2access_error)

        # B2access user info
        b2access_user, intuser, extuser = self.get_b2access_user_info(
            auth, b2access, b2access_token, b2access_refresh_token
        )
        if b2access_user is None and intuser is None:
            log.error(extuser)
            return self.send_errors(
                errors="Unable to retrieve user info from b2access",
            )

        b2access_email = b2access_user.data.get("email")
        log.info("B2ACCESS email = {}", b2access_email)

        imain = self.get_main_irods_connection()

        irods_user = self.get_irods_user_from_b2access(imain, b2access_email)

        if irods_user is None:
            err = "B2ACCESS credentials ({}) do not match any user in B2SAFE".format(
                b2access_email
            )
            log.error(err)
            return self.send_errors(err)

        # Update db to save the irods user related to this user account
        self.associate_object_to_attr(extuser, "irodsuser", irods_user)

        user_home = imain.get_user_home(irods_user)

        # If all is well, give our local token to this validated user
        local_token, jti = auth.create_token(auth.fill_payload(intuser))
        user = self.get_user()
        auth.save_token(user, local_token, jti)

        return self.response(
            {"token": local_token, "b2safe_user": irods_user, "b2safe_home": user_home}
        )


class B2accesProxyEndpoint(EudatEndpoint):
    """
    Allow refreshing current proxy (if invalid)
    using the stored b2access token (if still valid)
    """

    baseuri = "/auth"
    labels = ["eudat", "b2access"]
    depends_on = ["B2ACCESS_APPKEY"]

    @decorators.auth.require()
    @decorators.endpoint(
        path="/proxy",
        summary="Check and/or refresh current b2access proxy credentials",
        responses={200: "Refresh status"},
    )
    def post(self):

        ##########################
        # get the response
        r = self.init_endpoint()  # only_check_proxy=True)
        if r.errors is not None:
            return self.send_errors(errors=r.errors)

        ##########################
        # verify what happened
        if r.valid_credentials:
            if r.refreshed:
                return {"Expired": "New proxy was generated."}
            else:
                log.debug("Current user does not use a proxy")
                return {"Skipped": "Not using a certificate proxy."}

        return {"Info": "Unknown status."}
