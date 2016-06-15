# -*- coding: utf-8 -*-

""" CUSTOM Models for the relational database """

from __future__ import absolute_import
from ..sql import db, User

# from common.logs import get_logger
# logger = logging.get_logger(__name__)

# Add (inject) attributes to User
setattr(User, 'name', db.Column(db.String(255)))
setattr(User, 'surname', db.Column(db.String(255)))
