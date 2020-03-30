# -*- coding: utf-8 -*-

"""
Publish a digital object as a public resource for anyone

NOTE: this package will be loaded only if IRODS_ANONYMOUS is set
"""

from b2stage.apis.commons.endpoint import EudatEndpoint
from restapi import decorators
from restapi.exceptions import RestApiException
from b2stage.apis.commons import path
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


class Publish(EudatEndpoint):

    # schema_expose = True
    labels = ['eudat', 'publish']
    depends_on = ['IRODS_ANONYMOUS', 'ENABLE_PUBLIC_ENDPOINT']
    GET = {
        '/publish/<path:location>': {
            'custom': {},
            'summary': 'Check if the path is currently readable for the anonymous user',
            'responses': {'200': {'description': "return a boolean 'published'"}},
        }
    }
    PUT = {
        '/publish/<path:location>': {
            'custom': {},
            'summary': 'set the path to be readable for the anonymous user',
            'responses': {'200': {'description': "return a boolean 'published'"}},
        }
    }
    DELETE = {
        '/publish/<path:location>': {
            'custom': {},
            'summary': 'Ensure that the path is not accessible for the anonymous user',
            'responses': {'200': {'description': "return a boolean 'published'"}},
        }
    }

    def base(self, r, location):

        if location is None:
            raise RestApiException(
                'Location: missing filepath inside URI',
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        location = self.fix_location(location)

        if r.errors is not None:
            raise RestApiException(r.errors)

        path, resource, filename, _ = self.get_file_parameters(
            r.icommands, path=location
        )

        # Does this path exist?
        if not r.icommands.exists(path):
            raise RestApiException(
                "path {}not existing or no permissions".format(path),
                status_code=hcodes.HTTP_BAD_NOTFOUND,
            )

        return path

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

        current_zone = icom.get_current_zone()
        ipath_steps = path.parts(ipath)
        current = ''

        for ipath_step in ipath_steps:

            current = path.join(current, ipath_step, return_str=True)
            # print("PUB STEP:", ipath_step, current, len(current))

            # to skip: root dir, zone and home
            if (
                len(ipath_step) == 1
                or ipath_step == current_zone
                or ipath_step == 'home'
            ):
                continue

            # find out if already published
            check = self.single_path_check(icom, current_zone, str(current))
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

    @staticmethod
    def public_path(path):

        # prepare the url to access
        from b2stage.apis.commons import CURRENT_HTTPAPI_SERVER
        from b2stage.apis.commons import PUBLIC_ENDPOINT

        return '{}{}{}'.format(CURRENT_HTTPAPI_SERVER, PUBLIC_ENDPOINT, path)

    @decorators.catch_errors()
    @decorators.auth.required()
    def get(self, location):

        handler = self.init_endpoint()
        path = self.base(handler, location)

        icom = handler.icommands
        user = icom.get_current_user()
        log.info("user '{}' requested to check '{}'", user, path)

        if icom.is_collection(path):
            return self.send_errors(
                'Collections are not allowed to be published',
                code=hcodes.HTTP_BAD_REQUEST,
            )
        else:
            published = self.publish_helper(icom, path)
            response = {'published': published}
            if published:
                response['public_url'] = self.public_path(path)
            return response

    @decorators.catch_errors()
    @decorators.auth.required()
    def put(self, location=None):

        handler = self.init_endpoint()
        path = self.base(handler, location)

        icom = handler.icommands
        user = icom.get_current_user()
        log.info("user '{}' requested to publish '{}'", user, path)

        if icom.is_collection(path):
            return self.send_errors(
                'Collections are not allowed to be published',
                code=hcodes.HTTP_BAD_REQUEST,
            )

        # if already set as the same don't do anything
        if not self.publish_helper(icom, path):
            self.publish_helper(icom, path, check_only=False, unpublish=False)
        # # If you'd like to check again:
        # return {'published': self.publish_helper(icom, path)}

        return {'published': True, 'public_url': self.public_path(path)}

    @decorators.catch_errors()
    @decorators.auth.required()
    def delete(self, location):

        handler = self.init_endpoint()
        path = self.base(handler, location)

        icom = handler.icommands
        user = icom.get_current_user()
        log.info("user '{}' requested to UNpublish '{}'", user, path)

        if icom.is_collection(path):
            return self.send_errors(
                'Collections are not allowed to be published',
                code=hcodes.HTTP_BAD_REQUEST,
            )

        # if not already set as the same don't do anything
        if self.publish_helper(icom, path):
            self.publish_helper(icom, path, check_only=False, unpublish=True)

        # # If you'd like to check again:
        # return {'published': self.publish_helper(icom, path)}
        return {'published': False}
