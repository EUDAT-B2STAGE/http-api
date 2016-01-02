#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main server factory.
We create all the components here!
"""

from __future__ import division, absolute_import
from . import myself, lic, get_logger

from flask_admin import Admin
from flask import redirect
from flask_admin.contrib import sqla
from flask.ext.security import current_user
from flask.ext.restful import request, url_for, abort
from confs import config
from . import htmlcodes as hcodes

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

####################################
# Admininistration
admin = Admin(name='Adminer', url=config.ALL_API_URL+'/manage',
              template_mode='bootstrap3')
logger.debug("Flask: creating Admininistration")


#############################
# Create admin views
class MyModelView(sqla.ModelView):

    column_display_pk = True
    column_hide_backrefs = False

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role(config.ROLE_ADMIN):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """ Override builtin _handle_view to redirect users """
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(hcodes.HTTP_BAD_FORBIDDEN)  # permission denied
            else:  # login
                return redirect(url_for('security.login', next=request.url))


class RoleView(MyModelView):
    can_delete = False  # disable model deletion
    # can_edit = False


class UserView(MyModelView):
    column_searchable_list = ['first_name', 'email']
    column_filters = ['roles']
    column_editable_list = ['first_name', 'last_name']
    column_list = ('first_name', 'last_name', 'email', 'active', 'roles')
    edit_modal = True
    can_export = True
    # create_modal = True
    # column_exclude_list = ['password', 'confirmed_at']
    # form_ajax_refs = {'roles': {'fields': (Role.name,)}}
