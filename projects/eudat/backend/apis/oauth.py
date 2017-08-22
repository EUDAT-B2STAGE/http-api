# -*- coding: utf-8 -*-

"""
OAUTH inside EUDAT services
"""

from flask import url_for
from restapi.flask_ext.flask_irods.client import IrodsException
from restapi import decorators as decorate
# from utilities import htmlcodes as hcodes
from eudat.apis.common import PRODUCTION
# from eudat.apis.common.b2access import B2accessUtilities
from eudat.apis.common.b2stage import EudatEndpoint
from utilities.logs import get_logger

log = get_logger(__name__)


# class OauthLogin(B2accessUtilities):
class OauthLogin(EudatEndpoint):
    """
    Endpoint which redirects to B2ACCESS server online,
    to ask the current user for authorization/token.
    """

    @decorate.catch_error(
        exception=RuntimeError,
        exception_label='Server side B2ACCESS misconfiguration')
    def get(self):

        auth = self.auth
        b2access = self.create_b2access_client(auth)

        authorized_uri = url_for('authorize', _external=True)
        if PRODUCTION:
            # What needs a fix:
            # http://awesome.docker:443/auth/authorize
            # curl -i -k https://awesome.docker/auth/askauth
            authorized_uri = authorized_uri \
                .replace('http:', 'https:') \
                .replace(':443', '')

        log.info("Ask redirection to: %s" % authorized_uri)

        response = b2access.authorize(callback=authorized_uri)
        return self.force_response(response)


# class Authorize(B2accessUtilities):
class Authorize(EudatEndpoint):
    """
    Previous endpoint will redirect here if authorization was granted.
    Use the B2ACCESS token to retrieve info about the user,
    and to store the proxyfile.
    """

    @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
    def get(self):
        """
        Get the data for upcoming operations.

        Note: all of this actions are based on our user to have granted
        permissions to access his profile data.
        """

        # Get b2access token
        auth = self.auth
        b2access = self.create_b2access_client(auth, decorate=True)
        b2access_token, b2access_error = self.request_b2access_token(b2access)
        if b2access_token is None:
            return self.send_errors(message=b2access_error)

        # B2access user info
        curuser, intuser, extuser = \
            self.get_b2access_user_info(auth, b2access, b2access_token)
        if curuser is None and intuser is None:
            return self.send_errors('oauth2', extuser)

        # B2access user proxy
        proxy_file = self.obtain_proxy_certificate(auth, extuser)
        if proxy_file is None:
            return self.send_errors(
                "B2ACCESS CA is down", "Could not get certificate files")

        # iRODS related
        # NOTE: this irods client uses default admin to find the related user
        admin_icom = self.get_service_instance(
            service_name='irods', be_admin=True)
        uid = self.username_from_unity(curuser.data.get('unity:persistent'))
        irods_user = self.set_irods_username(admin_icom, auth, extuser, uid)
        if irods_user is None:
            log.warning(
                "Mismatching external user inside B2SAFE" +
                ": %s/%s" % (uid, extuser))
            return self.send_errors(
                "Current B2ACCESS credentials (%s) " % uid +
                "do not match any user inside B2SAFE namespace"
            )
        user_home = admin_icom.get_user_home(irods_user)

        # If all is well, give our local token to this validated user
        local_token, jti = auth.create_token(auth.fill_payload(intuser))
        auth.save_token(auth._user, local_token, jti)

        # # TOFIX: Workout a better way to get the host in this example
        # uri = self.httpapi_location(
        #     request.url.replace("/auth/authorize", ''),
        #     API_URL + "/namespace" + user_home
        # )
        # get_example = "curl -H 'Authorization: %s %s' %s" \
        #     % ('Bearer', local_token, uri)

        # TOFIX: Create a method to reply with standard Bearer oauth response
        # return self.send_credentials(local_token, extra, metas)

        return self.force_response(
            defined_content={
                'token': local_token,
                'b2safe_user': irods_user,
                'b2safe_home': user_home
            },
            # meta={
            #     'examples': {
            #         'get': get_example
            #     }
            # }
        )


class B2accesProxyEndpoint(EudatEndpoint):
    """
    Allow refreshing current proxy (if invalid)
    using the stored b2access token (if still valid)
    """

    def post(self):

        ##########################
        # get the response
        r = self.init_endpoint()  # only_check_proxy=True)
        log.pp(r)
        if r.errors is not None:
            return self.send_errors(errors=r.errors)

        ##########################
        # verify what happened
        if r.valid_credentials:
            if r.refreshed:
                return {"Expired": "New proxy was generated."}
            elif r.is_proxy:
                log.debug("A valid proxy already exists")
                return {"Verified": "Current proxy is valid."}
            else:
                log.debug("Current user does not use a proxy")
                return {"Skipped": "Not using a certificate proxy."}

        return {"Info": "Unknown status."}


#######################################
# JUST TO TEST
#######################################

# # class TestB2access(B2accessUtilities):
# class TestB2access(EudatEndpoint):
#     """ development tests """

#     @decorate.catch_error(exception=IrodsException, exception_label='B2SAFE')
#     def get(self):

#         ##########################
#         # get the response
#         r = self.init_endpoint()
#         # log.pp(r)
#         if r.errors is not None:
#             return self.send_errors(errors=r.errors)
#         log.pp(r)

#         ##########################
#         return {'list': r.icommands.list()}
