#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main server factory.
We create all the components here!
"""

from __future__ import division, absolute_import
from . import myself, lic, get_logger

from flask.ext.security import SQLAlchemyUserDatastore  # , Security
from .models import db, User, Role
from confs import config

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

####################################
# Security
udstore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(datastore=udstore)


####################################
# DB init for security
def db_auth():
    """ What to do if the main auth object has no rows """

    missing_role = not Role.query.first()
    logger.debug("Missing role")
    if missing_role:
        udstore.create_role(name=config.ROLE_ADMIN, description='King')
        udstore.create_role(name=config.ROLE_USER, description='Citizen')
        logger.debug("Created roles")

    missing_user = not User.query.first()
    logger.debug("Missing user")
    if missing_user:
        from flask_security.utils import encrypt_password
        udstore.create_user(first_name='User', last_name='IAm',
                            email=config.USER,
                            password=encrypt_password(config.PWD))
        udstore.add_role_to_user(config.USER, config.ROLE_ADMIN)
        logger.debug("Created user")

    if missing_user or missing_role:
        db.session.commit()
        logger.info("Database init with user/roles from conf")
