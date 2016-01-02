# -*- coding: utf-8 -*-
"""
A secured app from:
https://pythonhosted.org/Flask-Security/quickstart.html
Using the blog post:
http://mandarvaze.github.io/2015/01/token-auth-with-flask-security.html

To check your sqllite db:
$ docker run -it -v (pwd):/code -p 80:80 clue/adminer
Then go into your browser, choose sqllite3 and file is /code/YOURDB.db

To test token with httpie:
http yourhost:8888/login email=test@test.it password=password
http yourhostwesome.dev:8888/authtest Authentication-Token:TOKENRECEIVED
# If you have admin role:
http yourhostwesome.dev:8888/admin Authentication-Token:TOKENRECEIVED

"""

####################################
import os
from flask import Flask

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api, Resource
from flask.ext.security \
    import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, roles_required, auth_token_required

# INIT DATA
USER = 'test@test.it'
PWD = 'password'
ROLE_ADMIN = 'adminer'

####################################
# CONFIGURATION
DEBUG = True
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
dbfile = os.path.join(BASE_DIR, 'testsecurity.db')
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
SECURITY_PASSWORD_SALT = "ifiwantobeinproductionihavetousesecretsalt"

####################################
# Create app
app = Flask(__name__)
# Load configuration from above
app.config.from_object(__name__)
# Add REST resources
api = Api(app)
# Create database connection object
db = SQLAlchemy(app)


####################################
# Define models
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

roles_users = \
    db.Table('roles_users',
             db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
             db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


# Note: do not use 'User' as it may mix with postgresql keyword
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    auth_token = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))


####################################
# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, Users, Role)
security = Security(app, user_datastore)

####################################
try:
    db.create_all()
    print("Connected")
    # Create a user to test with
    if not Users.query.first():
        user_datastore.create_user(email=USER, password=PWD)
        user_datastore.create_role(name=ROLE_ADMIN, description='I am Master')
        # user_datastore.find_or_create_role(ROLE_ADMIN)
        user_datastore.add_role_to_user(USER, ROLE_ADMIN)
        print("Database initizialized")
        db.session.commit()
except Exception as e:
    print("Database connection failure: %s" % str(e))


####################################
# Views
@app.route('/')
def home():
    return "Hello world", 200


####################################
# API restful test
class AuthTest(Resource):

    @auth_token_required
    def get(self):
        ret_dict = {"Key1": "Value1", "Key2": "value2"}
        return ret_dict, 200


class Admin(Resource):

    @auth_token_required
    @roles_required(ROLE_ADMIN)  # , 'another')
    def get(self):
        # return abort(404, message='NO!')
        return "I am admin!"

api.add_resource(AuthTest, '/' + AuthTest.__name__.lower())
api.add_resource(Admin, '/' + Admin.__name__.lower())
print("REST Resources ready")

#############################
if __name__ == '__main__':
    app.run(host=HOST)
