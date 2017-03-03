# -*- coding: utf-8 -*-

""" CUSTOM Models for the relational database """

from rapydo.models.sql import db, User, ExternalAccounts

# from common.logs import get_logger
# logger = logging.get_logger(__name__)

# Add (inject) attributes to User
## TO FIX: should this already be there or what?
setattr(User, 'name', db.Column(db.String(255)))
setattr(User, 'surname', db.Column(db.String(255)))

# Let iRODS exist and be linked
setattr(ExternalAccounts, 'irodsuser', db.Column(db.String(50)))
# Also save the unity persistent identifier from EUDAT
setattr(ExternalAccounts, 'unity', db.Column(db.String(100)))
