# -*- coding: utf-8 -*-

""" Database models """

import importlib
from datetime import datetime
from config import user_config
from collections import OrderedDict
from flask import url_for, request
from flask.ext.table import Table, Col, create_table
from flask.ext.login import LoginManager
from sqlalchemy import inspect
from flask.ext.sqlalchemy import SQLAlchemy


#############################################
# http://piotr.banaszkiewicz.org/blog/2012/06/30/serialize-sqlalchemy-results-into-json/ 
class DictSerializable(object):
    """ An object to keep an ordered version of ORM model attributes """
    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result

#############################################
# DB INIT

# no app object passed! Instead we use use db.init_app in the factory.
db = SQLAlchemy()
# Flask LOGIN
lm = LoginManager()


#############################################
# USER MODEL: necessary for Login
class User(db.Model):

    __tablename__ = "users"

    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20),
                         unique=True, index=True)
    password = db.Column('password', db.String(20))
    email = db.Column('email', db.String(50), unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


#############################################
# Convert an SQLALCHEMY model into a Flask table
class AnchorCol(Col):
    def td_format(self, content):
        return '<a href="/view/' + content + '">' + content + '</a>'


class ItemTable(Table):

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for(request.endpoint, sort=col_key, direction=direction)


def model2list(obj):
    mylist = []
    for column in inspect(obj).attrs:
        mylist.append(column.key)
    return mylist


def model2table(obj, selected):
    """ Give me an SQLALCHEMY obj to get an HTML table """

    table_name = 'Table' + obj.__name__
    TableCls = create_table(table_name, base=ItemTable)
    mapper = inspect(obj)

    for column in mapper.attrs:

        # What to skip
        if selected and column.key not in selected:
            continue

        colname = column.key.replace('_', ' ').capitalize()
        if column.key == 'id':  # 'patient_id':
            TableCls.add_column(column.key, AnchorCol(colname))
        else:
            TableCls.add_column(column.key, Col(colname))

    TableCls.classes = ['table', 'table-hover']
    TableCls.thead_classes = ["thead-default"]
    TableCls.allow_sort = True

    return TableCls

##################################################
# WHERE THE MAGIC HAPPENS: dynamic models, and tables
package = __package__ + '.models.' + user_config['models']['module']
module = importlib.import_module(package)
selected_model = user_config['models'].get('model', 'MyModel')
MyModel = getattr(module, selected_model)

#########################################################
# Build dynamic table

# From configuration, choose table and insert fields
insertable = user_config['models'].get('insert_fields')
extra_selected = user_config['models'].get('extra_fields_to_show', [])
if insertable:
    selected = extra_selected + insertable
# If configuration has no options
else:
    selected = model2list(MyModel)
    insertable = selected

# Build the main table for the view
MyTable = model2table(MyModel, selected)
