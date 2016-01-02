#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Testing flask admin """

#############################
import os
from flask import Flask

from flask.ext.sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(BASE_DIR, 'testmodels.db')
# flask conf
DEBUG = True
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))
SECRET_KEY = 'my precious'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + dbfile
SQLALCHEMY_TRACK_MODIFICATIONS = False

#############################
# Create application
app = Flask(__name__, template_folder=BASE_DIR)
app.config.from_object(__name__)
db = SQLAlchemy(app)


#############################
# Setup app and create models here
class User(db.Model):
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(20))
    email = db.Column('email', db.String(50), unique=True, index=True)

db.drop_all()
db.create_all()

#############################
admin = Admin(app, name='microblog', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))

#############################
if __name__ == '__main__':
    app.run(host=HOST, debug=True)
