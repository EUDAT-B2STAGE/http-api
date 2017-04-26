# -*- coding: utf-8 -*-

""" CUSTOM Models for the relational database """

from __future__ import absolute_import
from ..sql import db, ExternalAccounts  # , User

# from common.logs import get_logger
# logger = logging.get_logger(__name__)

# # Add (inject) attributes to User
# setattr(User, 'name', db.Column(db.String(255)))
# setattr(User, 'surname', db.Column(db.String(255)))

# Let iRODS exist and be linked
setattr(ExternalAccounts, 'irodsuser', db.Column(db.String(50)))
# Also save the unity persistent identifier from EUDAT
setattr(ExternalAccounts, 'unity', db.Column(db.String(100)))
