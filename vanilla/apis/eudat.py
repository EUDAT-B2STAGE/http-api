# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
"""

from __future__ import absolute_import

import os
import json
from plumbum.commands.processes import ProcessExecutionError as perror
from flask import url_for
from confs.config import AUTH_URL
from ..base import ExtendedApiResource
from ..services.irods.client import IrodsException
from ..services.uploader import Uploader
from ..services.oauth2clients import decorate_http_request
from commons import htmlcodes as hcodes
from ...auth import auth
from .. import decorators as decorate

from ... import get_logger
logger = get_logger(__name__)


# def after_this_request(f):
#     if not hasattr(g, 'after_request_callbacks'):
#         g.after_request_callbacks = []
#     g.after_request_callbacks.append(f)
#     return f

def handle_collection_path(self, icom, ipath):
    """
    iRODS specific pattern to handle paths
    """

    home = icom.get_base_dir()

    # Should add the base dir if doesn't start with /
    if ipath is None or ipath == '':
        ipath = home
    elif ipath[0] != '/':
        ipath = home + '/' + ipath
    else:
        # Add the zone
        ipath = '/' + icom._current_environment['IRODS_ZONE'] + ipath
    # Append / if missing in the end
    if ipath[-1] != '/':
        ipath += '/'

    return ipath


###############################
# Classes

class OauthLogin(ExtendedApiResource):
    """ API online test """

    base_url = AUTH_URL

    @decorate.apimethod
    def get(self):

        auth = self.global_get('custom_auth')
        b2access = auth._oauth2.get('b2access')
        response = b2access.authorize(
            callback=url_for('authorize', _external=True))
        return self.response(response)


class Authorize(ExtendedApiResource):
    """ API online test """

    base_url = AUTH_URL

    @decorate.apimethod
    def get(self):

        auth = self.global_get('custom_auth')
        b2access = auth._oauth2.get('b2access')
        # B2ACCESS requires some fixes to make this authorization call
        decorate_http_request(b2access)

        resp = None
        try:
            resp = b2access.authorized_response()

        except json.decoder.JSONDecodeError as e:
            logger.critical("Authorization empty:\n%s\nCheck app credentials"
                            % str(e))
            return self.response({'errors': [{'Server misconfiguration':
                                 'oauth2 failed'}]})

        except Exception as e:
            # raise e
            logger.critical("Failed to get authorized response:\n%s" % str(e))
            return self.response(
                {'errors': [{'Access denied': 'B2ACCESS OAUTH2: ' + str(e)}]})

        if resp is None:
            return self.response(
                {'errors': [{'Access denied': 'Uknown error'}]})

        token = resp.get('access_token')
        if token is None:
            logger.critical("No token received")
        else:
            logger.info("Received token: '%s'" % token)

            # Use b2access with token to get user info
            # ## http://j.mp/b2access_profile_attributes
            from flask import session
            session['b2access_token'] = (token, '')
            current_user = b2access.get('userinfo')

            # Store b2access information inside the graphdb
            graph = self.global_get_service('neo4j')
            obj = graph.save_oauth2_info_into_user(
                graph, current_user, token)
## // TO FIX:
# make this a 'check_if_error_obj' inside the ExtendedAPIResource
            if isinstance(obj, dict) and 'errors' in obj:
                return self.response(obj)
            user_node = obj
            logger.info("Stored access info")

            # Get a valid certificate to access irods
            from commons.certificates import Certificates
            b2accessCA = auth._oauth2.get('b2accessCA')
            obj = Certificates().make_proxy_from_ca(b2accessCA)
            if isinstance(obj, dict) and 'errors' in obj:
                return self.response(obj)
            logger.info("Created proxy")

# ADD USER (if not exists) IN CASE WE ARE USING A DOCKERIZED VERSION
            # To do
            from ..services.detect import IRODS_EXTERNAL
            if IRODS_EXTERNAL:
                print("ADD/CHECK USER INSIDE IRODS")

            # Create a valid token for our API
            token = auth.create_token(auth.fill_payload(user_node))

## // TO FIX:
# Create a return_credentials method for Bearer ?
        return self.response({'token': token})


class CollectionEndpoint(ExtendedApiResource):

    @auth.login_required
    @decorate.apimethod
    def get(self, path=None):
        """
        Return list of elements inside a collection.
        If path is not specified we list the home directory.
        """

# CHECK IF TOKEN IS AVAILABLE?
        # if 'b2access_token' in session:
# CHECK IF TOKEN IS VALID?

        auth = self.global_get('custom_auth')
        print("DEBUG PROFILE", auth._user, auth._payload)

        icom = self.global_get_service('irods')  # , user='paolo')
        return self.response(icom.list(path))

    @auth.login_required
    @decorate.add_endpoint_parameter('collection', required=True)
    @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.apimethod
    def post(self):
        """ Create one collection/directory """

        icom = self.global_get_service('irods')
        ipath = self._args.get('collection')

        try:
            icom.create_empty(
                ipath, directory=True, ignore_existing=self._args.get('force'))
            logger.info("irods made collection: %s", ipath)
        except perror as e:
            # ##HANDLING ERROR
# // TO FIX: use a decorator
            error = str(e)
            if 'ERROR:' in error:
                error = error[error.index('ERROR:') + 7:]
            return self.response(errors={'iRODS error': error})

        return self.response(ipath, code=hcodes.HTTP_OK_CREATED)


class DataObjectEndpoint(Uploader, ExtendedApiResource):

    @auth.login_required
    @decorate.add_endpoint_parameter('collection')
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def get(self, name=None):
        """
        Get object from ID

        Note to self:
        we need to get the username from the token
        """

        if name is None or name[-1] == '/':
            return self.response(
                errors={'dataobject': 'No dataobject/file requested'})

        # obj init
        user = self.get_token_user()
        icom = self.global_get_service('irods')

        # paths
        collection = handle_collection_path(
            icom, self._args.get('collection'))
        ipath = collection + name
        abs_file = self.absolute_upload_file(name, user)

        try:
            os.remove(abs_file)
        except:
            pass

        # Execute icommand
        icom.open(ipath, abs_file)

        # Download the file from local fs
        filecontent = super().download(
            name, subfolder=user, get=True)

        # Remove local file
        os.remove(abs_file)

        # Stream file content
        return filecontent

    @auth.login_required
    @decorate.add_endpoint_parameter('collection')
    @decorate.apimethod
    @decorate.catch_error(exception=IrodsException, exception_label='iRODS')
    def post(self):
        """
        Handle file upload
        """

        user = self.get_token_user()

        # Original upload
        response = super(DataObjectEndpoint, self).upload(subfolder=user)

        # If response is success, save inside the database
        key_file = 'filename'
        filename = None

        content = self.get_content_from_response(response)
        errors = self.get_content_from_response(response, get_error=True)
        status = self.get_content_from_response(response, get_status=True)

        if isinstance(content, dict) and key_file in content:
            filename = content[key_file]
            abs_file = self.absolute_upload_file(filename, user)
            logger.info("File is '%s'" % abs_file)

            ############################
            # Move file inside irods
            icom = self.global_get_service('irods')

            # ##HANDLING PATH
            # The home dir for the current user
            # Where to put the file in irods
            collection = handle_collection_path(
                icom, self._args.get('collection'))
            ipath = collection + filename

            try:
                iout = icom.save(abs_file, destination=ipath)
                logger.info("irods call %s", iout)
            except IrodsException as e:
                # Remove local cache if i could not save on irods
                os.remove(abs_file)
                raise e

            # Remove actual file (if we do not want to cache)
            os.remove(abs_file)
            content = {
                'collection': ipath
            }

        # Reply to user
        return self.response(data=content, errors=errors, code=status)

    @auth.login_required
    @decorate.add_endpoint_parameter('collection')
    @decorate.apimethod
    def delete(self, name):
        """ Remove an object """

        icom = self.global_get_service('irods')
        # paths
        collection = handle_collection_path(
            icom, self._args.get('collection'))
        ipath = collection + name
        try:
            iout = icom.remove(ipath)
            logger.info("irods call %s", iout)
        except perror as e:
            error = str(e)
            if 'ERROR:' in error:
                error = error[error.index('ERROR:') + 7:]
            return self.response(errors={'iRODS error': error})

        return self.response({'deleted': ipath})
