# -*- coding: utf-8 -*-

"""
Publish a digital object as a public resource for anyone

NOTE: this package will be loaded only if IRODS_ANONYMOUS is set
"""

from utilities import htmlcodes as hcodes
from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi import decorators as decorate
from utilities.logs import get_logger

log = get_logger(__name__)


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

        # Does this path exist?
        if not r.icommands.exists(path):
            return self.send_errors(
                errors=[{
                    'path': "'%s': not existing or no permissions" % path
                }], code=hcodes.HTTP_BAD_NOTFOUND), \
                None, None

        return None, r, path

    def single_path_check(self, icom, zone, abs_path, check=True):

        permissions = icom.get_permissions(abs_path)
        acls = permissions.get('ACL', [])

        published = False
        for acl_user, acl_zone, acl_mode in acls:
            if acl_zone == zone and acl_user == icom.anonymous_user:
                if check:
                    if 'read' in acl_mode:
                        published = True
                        break

        return published

    def single_permission(self, icom, ipath, permission=None):

        icom.set_permissions(
            ipath,
            # NOTE: permission could be: read, write, null/None
            permission=permission,
            userOrGroup=icom.anonymous_user,
        )  # , recursive=False)
        # FIXME: should we publish recursively to subfiles and subfolders?
        # NOTE: It looks dangerous to me

    def publish_helper(self, icom, ipath, check_only=True, unpublish=False):

        from utilities import path
        current_zone = icom.get_current_zone()
        ipath_steps = path.parts(ipath)
        current = ''

        for ipath_step in ipath_steps:

            current = path.join(current, ipath_step, return_str=True)
            # print("PUB STEP:", ipath_step, current, len(current))

            # to skip: root dir, zone and home
            if len(ipath_step) == 1 \
               or ipath_step == current_zone or ipath_step == 'home':
                continue

            # find out if already published
            check = self.single_path_check(
                icom, current_zone, str(current))
            # if only checking
            if check_only and not check:
                return False
            # otherwise you want to publish/unpublish this path
            else:
                if unpublish:
                    self.single_permission(icom, current, permission=None)
                else:
                    self.single_permission(icom, current, permission='read')

        return True

    @decorate.catch_error()
    def get(self, irods_location):

        error, handler, path = self.base(irods_location)
        if error is not None:
            return error

        icom = handler.icommands
        user = icom.get_current_user()
        log.info("user '%s' requested to check '%s'", user, path)
        return {'published': self.publish_helper(icom, path)}

    @decorate.catch_error()
    def put(self, irods_location=None):

        error, handler, path = self.base(irods_location)
        if error is not None:
            return error

        icom = handler.icommands
        user = icom.get_current_user()
        log.info("user '%s' requested to publish '%s'", user, path)

        # if already set as the same don't do anything
        if not self.publish_helper(icom, path):
            self.publish_helper(icom, path, check_only=False, unpublish=False)

        # # If you'd like to check again:
        # return {'published': self.publish_helper(icom, path)}
        return {'published': True}

    @decorate.catch_error()
    def delete(self, irods_location):

        error, handler, path = self.base(irods_location)
        if error is not None:
            return error

        icom = handler.icommands
        user = icom.get_current_user()
        log.info("user '%s' requested to UNpublish '%s'", user, path)

        # if not already set as the same don't do anything
        if self.publish_helper(icom, path):
            self.publish_helper(icom, path, check_only=False, unpublish=True)

        # # If you'd like to check again:
        # return {'published': self.publish_helper(icom, path)}
        return {'published': False}
