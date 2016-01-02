#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" User defined model """

from ..basemodel import db
from wtforms.validators import Email, Length
from wtforms import PasswordField

#############################################
# Work on models
class MyModel(db.Model):

    # Primary key
    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True)
    # Normal
    name = db.Column(db.Unicode(5), nullable=False,
                     info={'validators': Length(min=5, max=255)})
    # Custom validator
    email = db.Column(db.Unicode(255), nullable=False,
                      info={'validators': Email()})
    # Test SELECT
    # enum sqlalchemy tutorial
    # http://techspot.zzzeek.org/2011/01/14/the-enum-recipe/
    test_select_a = db.Column(db.Enum(
        'part_time', 'full_time', 'contractor', name='employee_types'))
    # Password field from WTForm types
    password = db.Column(db.String(255),
                         info={'form_field_class': PasswordField})
