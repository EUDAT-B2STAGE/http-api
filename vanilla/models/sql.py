# -*- coding: utf-8 -*-

""" CUSTOM Models for the relational database """

from __future__ import absolute_import
from ..sql import db, \
    User as UserBase  # , roles_users

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class User(UserBase):
    """ Adding attributes to the original class """

    name = db.Column(db.String(255))
    surname = db.Column(db.String(255))
