# -*- coding: utf-8 -*-

"""
B2SAFE HTTP REST API endpoints.
"""

import os
from ..base import ExtendedApiResource
from .. import decorators as decorate
from ..services.irods.client import ICommands, IrodsException
from ..services.uploader import Uploader
from plumbum.commands.processes import ProcessExecutionError as perror
from ... import htmlcodes as hcodes
from flask import url_for, request  # , g
from confs.config import AUTH_URL
from ...auth import auth
from ..services.oauth2clients \
    import ExternalServicesLogin, decorate_http_request

from ... import get_logger
logger = get_logger(__name__)


# def after_this_request(f):
#     if not hasattr(g, 'after_request_callbacks'):
#         g.after_request_callbacks = []
#     g.after_request_callbacks.append(f)
#     return f


###############################
# Classes

class OauthLogin(ExtendedApiResource):
    """ API online test """

    base_url = AUTH_URL

    @decorate.load_auth_obj
    def get(self):

        b2access = self._auth._oauth2['b2access']
        print("TEST", b2access)
        out = "Hello"
        # out = b2access.authorize(
        #     callback=url_for('authorize', _external=True))
        print("AUTORIZED?", out)
        return out


class Authorize(ExtendedApiResource):
    """ API online test """

    base_url = AUTH_URL

    @decorate.apimethod
    def get(self):
        b2access = self._auth._oauth2['b2access']
        # B2ACCESS requires some fixes to make this authorization call
        decorate_http_request(b2access)

        resp = None
        try:
            resp = b2access.authorized_response()
        except Exception as e:
            print("ERROR", str(e))

        if resp is None:
            return self.response({
                'errors': "Access denied: reason=%s error=%s" % (
                    request.args['error'],
                    request.args['error_description']
                )})

        token = resp.get('access_token')
        if token is None:
            logger.critical("No token received")
        else:
            logger.info("Received token: '%s'" % token)

# SAVE THIS INTO DATABASE

        # If you want to save this into a cookie
        # @after_this_request
        # def set_cookie(response):
        #     response.set_cookie('access_token', token)
        #     print("SET COOKIE", response)

        # me = b2access.get('user')
        # return self.response(me.data)
        return self.response({'token': token})


class IrodsEndpoints(ExtendedApiResource):

    def get_token_user(self):
        """
        WARNING: NOT IMPLEMENTED YET!

        This will depend on B2ACCESS authentication
        """
################
#// TO FIX: this should be recovered from the JWT token
################
        return 'guest'

    def get_instance(self):
        user = self.get_token_user()
        # iRODS object
        return ICommands(user)

    def handle_collection_path(self, icom, ipath):

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


class CollectionEndpoint(IrodsEndpoints):

    @auth.login_required
    @decorate.apimethod
    def get(self, path=None):
        """
        Return list of elements inside a collection.
        If path is not specified we list the home directory.
        """

        icom = self.get_instance()
        return self.response(icom.list(path))

    @auth.login_required
    @decorate.add_endpoint_parameter('collection', required=True)
    @decorate.add_endpoint_parameter('force', ptype=bool, default=False)
    @decorate.apimethod
    def post(self):
        """ Create one collection/directory """

        icom = self.get_instance()
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


class DataObjectEndpoint(Uploader, IrodsEndpoints):

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
        icom = self.get_instance()

        # paths
        collection = self.handle_collection_path(
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
            icom = self.get_instance()

            # ##HANDLING PATH
            # The home dir for the current user
            # Where to put the file in irods
            collection = self.handle_collection_path(
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

        icom = self.get_instance()
        # paths
        collection = self.handle_collection_path(
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
