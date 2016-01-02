# -*- coding: utf-8 -*-
"""
Token authentication coupled with user admin interface endpoints

https://github.com/flask-admin/flask-admin/blob/master/examples/auth
"""

####################################
import os
from flask import Flask, redirect, url_for
# SQL
from flask.ext.sqlalchemy import SQLAlchemy
# REST classes
from flask.ext.restful import Api, Resource, abort, request
# Authentication
from flask.ext.security \
    import Security, SQLAlchemyUserDatastore, current_user, \
    UserMixin, RoleMixin, roles_required, auth_token_required
from flask_security.utils import encrypt_password

# Admin interface
from flask_admin import Admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
# The base user
USER = 'test@test.it'
PWD = 'pwd'

####################################
# CONFIGURATION
DEBUG = True
ROLE_ADMIN = 'adminer'
ROLE_USER = 'justauser'

HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(BASE_DIR, 'latest.db')
SECRET_KEY = 'my-super-secret-keyword'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + dbfile
SQLALCHEMY_TRACK_MODIFICATIONS = False
# Bug fixing for csrf problem via CURL/token
WTF_CSRF_ENABLED = False
# Force token to last not more than one hour
SECURITY_TOKEN_MAX_AGE = 3600
# Add security to password
# https://pythonhosted.org/Flask-Security/configuration.html
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "thishastobelongenoughtosayislonglongverylong"

####################################
# Create app
app = Flask(__name__, template_folder=BASE_DIR)
# Load configuration from above
app.config.from_object(__name__)
# Add REST resources
api = Api(app)
# Create database connection object
db = SQLAlchemy(app)
# Admininistration
admin = Admin(app, name='mytest', template_mode='bootstrap3')

####################################
# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


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
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


####################################
# Setup Flask-Security
udstore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, udstore)


####################################
# Prepare database and tables
try:
    db.drop_all()
    db.create_all()
    print("DB: Connected and ready")
except Exception as e:
    print("Database connection failure: %s" % str(e))


@app.before_first_request
def database_init():

    # Create a user to test with
    if not User.query.first():
        try:
            udstore.create_role(name=ROLE_ADMIN, description='I am Master')
            udstore.create_role(name=ROLE_USER, description='I am Normal')
            udstore.create_user(
                first_name='User', last_name='IAm',
                email=USER, password=encrypt_password(PWD))
            udstore.add_role_to_user(USER, ROLE_ADMIN)
            db.session.commit()
        except Exception as e:
            print("DB init fail: %s" % str(e))
        print("Database initizialized")


####################################
# API restful
@api.resource('/', '/hello')
class Hello(Resource):
    """ Example with no authentication """
    def get(self):
        return "Hello world", 200


class AuthTest(Resource):
    """ Token authentication test """

    @auth_token_required
    def get(self):
        ret_dict = {"Key1": "Value1", "Key2": "value2"}
        return ret_dict, 200


class Restricted(Resource):
    """ Token and Role authentication test """

    @auth_token_required
    @roles_required(ROLE_ADMIN)  # , 'another')
    def get(self):
        # return abort(404, message='NO!')
        return "I am admin!"

api.add_resource(AuthTest, '/' + AuthTest.__name__.lower())
api.add_resource(Restricted, '/' + Restricted.__name__.lower())
print("REST Resources ready")


#############################
# Create admin views
class MyModelView(sqla.ModelView):

    column_display_pk = True
    column_hide_backrefs = False

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role(ROLE_ADMIN):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """ Override builtin _handle_view to redirect users """
        if not self.is_accessible():
            if current_user.is_authenticated:
                abort(403)  # permission denied
            else:  # login
                return redirect(url_for('security.login', next=request.url))


class RoleView(MyModelView):
    can_delete = False  # disable model deletion
    # can_edit = False


class UserView(MyModelView):
    column_searchable_list = ['first_name', 'email']
    column_filters = ['roles']
    column_editable_list = ['first_name', 'last_name']
    column_list = ('first_name', 'last_name', 'email', 'active', 'roles')
    edit_modal = True
    can_export = True
    # create_modal = True
    # column_exclude_list = ['password', 'confirmed_at']
    # form_ajax_refs = {'roles': {'fields': (Role.name,)}}

admin.add_view(UserView(User, db.session))
admin.add_view(RoleView(Role, db.session))


# Define a context processor for merging flask-admin's template context
# into the flask-security views
@security.context_processor
def security_context_processor():
    return dict(admin_base_template=admin.base_template,
                admin_view=admin.index_view, h=admin_helpers)


#############################
if __name__ == '__main__':
    app.run(host=HOST)
