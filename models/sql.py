# -*- coding: utf-8 -*-

""" CUSTOM Models for the relational database """

from __future__ import absolute_import
from ..sql import db, User

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add (inject) attributes to User
setattr(User, 'name', db.Column(db.String(255)))
setattr(User, 'surname', db.Column(db.String(255)))
