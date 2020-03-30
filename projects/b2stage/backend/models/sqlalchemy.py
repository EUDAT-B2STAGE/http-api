# -*- coding: utf-8 -*-

""" CUSTOM Models for the relational database """

from restapi.models.sqlalchemy import db, User

# Add (inject) attributes to User
# setattr(User, 'name', db.Column(db.String(255)))
# setattr(User, 'surname', db.Column(db.String(255)))
setattr(User, 'session', db.Column(db.LargeBinary()))


class ExternalAccounts(db.Model):
    username = db.Column(db.String(60), primary_key=True)
    account_type = db.Column(db.String(16))
    token = db.Column(db.Text())
    refresh_token = db.Column(db.Text())
    token_expiration = db.Column(db.DateTime)
    email = db.Column(db.String(255))
    certificate_cn = db.Column(db.String(255))
    certificate_dn = db.Column(db.Text())
    proxyfile = db.Column(db.Text())
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # Let iRODS exist and be linked
    irodsuser = db.Column(db.String(50))
    # Also save the unity persistent identifier from EUDAT
    unity = db.Column(db.String(100))
    # Note: for pre-production release
    # we allow only one external account per local user
    main_user = db.relationship(
        'User', backref=db.backref('authorization', lazy='dynamic')
    )

    def __str__(self):
        return "db.{}({}, {})[{}]".format(
            self.__class__.__name__,
            self.username,
            self.email,
            self.main_user,
        )

    def __repr__(self):
        return self.__str__()
