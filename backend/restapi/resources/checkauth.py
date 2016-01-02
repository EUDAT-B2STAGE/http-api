#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SECURITY ENDPOINTS CHECK
Add auth checks called /checklogged and /testadmin
"""

from __future__ import division, absolute_import
from .. import myself, lic, get_logger
from .base import ExtendedApiResource
from . import decorators as decorate
from flask.ext.security import roles_required, auth_token_required
from confs import config

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)


class CheckLogged(ExtendedApiResource):
    """ Token authentication test """

    @decorate.apimethod
    @auth_token_required
    def get(self):
        return "Valid user"


class TestAdmin(ExtendedApiResource):
    """ Token and Role authentication test """

    @decorate.apimethod
    @auth_token_required
    @roles_required(config.ROLE_ADMIN)
    def get(self):
        return "I am admin!"
