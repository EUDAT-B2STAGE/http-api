#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Models for the relational database """

from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import UserMixin, RoleMixin

try:
    from . import get_logger
except:
    try:
        from config import get_logger
    except:
        print("Failed to found a logger")
        import sys
        sys.exit(1)

logger = get_logger(__name__)

####################################
# Create database connection object
db = SQLAlchemy()
logger.debug("Flask: creating SQLAlchemy")

####################################
# Define multi-multi relation
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


####################################
# Define models
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    registered_on = db.Column(db.DateTime)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __init__(self, **keyargs):
        self.registered_on = datetime.utcnow()
        super(User, self).__init__(**keyargs)

    def __repr__(self):
        return '<User %r>' % (self.email)

    def __str__(self):
        return self.email

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

logger.info("Loaded models")
