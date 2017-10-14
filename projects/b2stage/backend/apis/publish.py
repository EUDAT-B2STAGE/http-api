# -*- coding: utf-8 -*-

""" Publish a digital object as a public file for anyone """

from utilities import htmlcodes as hcodes
from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi import decorators as decorate
from utilities.logs import get_logger

log = get_logger(__name__)


# class Publish(EndpointResource):
class Publish(EudatEndpoint):

    def base(self, irods_location):

        if irods_location is None:
            return self.send_errors(
                'Location: missing filepath inside URI',
                code=hcodes.HTTP_BAD_REQUEST
            ), None, None
        else:
            irods_location = self.fix_location(irods_location)

        r = self.init_endpoint()
        if r.errors is not None:
            return self.send_errors(errors=r.errors), None, None

        path, resource, filename, _ = \
            self.get_file_parameters(r.icommands, path=irods_location)

        # if r.icommands.is_collection(path):
        #     return self.send_errors(
        #         'Provided path is a collection. ' +
        #         'Publishing is not allowed as recursive.',
        #         code=hcodes.HTTP_NOT_IMPLEMENTED
        #     ), None, None

        return None, r, path

    def check_published(self, acls, icom):

        published = False
        current_zone = icom.get_current_zone()

        for acl in acls:
            acl_user, acl_zone, acl_mode = acl
            if acl_zone == current_zone:
                if acl_user == icom.anonymous_user:
                    if 'read' in acl_mode:
                        published = True
                        break
        return published

    @decorate.catch_error()
    def get(self, irods_location):

        error, handler, path = self.base(irods_location)
        if error is not None:
            return error

        icom = handler.icommands
        user = icom.get_current_user()
        log.info("user '%s' requested to check '%s'", user, path)

        permissions = icom.get_permissions(path)
        log.pp(permissions)

        published = self.check_published(permissions.get('ACL', []), icom)
        return {'published': published}

    @decorate.catch_error()
    def put(self, irods_location=None):

        error, handler, path = self.base(irods_location)
        if error is not None:
            return error

        icom = handler.icommands
        user = icom.get_current_user()
        log.info("user '%s' requested to publish '%s'", user, path)

        # FIXME: it should be applied to all directories in path (from homedir)

        # if already set as the same don't do anything
        permissions = icom.get_permissions(path)
        # log.pp(permissions)
        if not self.check_published(permissions.get('ACL', []), icom):
            icom.set_permissions(
                path,
                permission='read',
                userOrGroup=icom.anonymous_user,
            )  # , recursive=False)

        return {'published': True}

    @decorate.catch_error()
    def delete(self, irods_location):

        error, handler, path = self.base(irods_location)
        if error is not None:
            return error

        icom = handler.icommands
        user = icom.get_current_user()
        log.info("user '%s' requested to unpublish '%s'", user, path)

        # if already set as the same don't do anything
        permissions = icom.get_permissions(path)
        # log.pp(permissions)
        if self.check_published(permissions.get('ACL', []), icom):
            icom.set_permissions(
                path, permission=None, userOrGroup=icom.anonymous_user,)

        return {'published': False}
