# -*- coding: utf-8 -*-

""" Main routes """

import requests
import json
# import commentjson as json
# import simplejson as json
from datetime import datetime
# from flask import Response, stream_with_context
from flask.ext.login import login_user, UserMixin
from config import BACKEND
from .basemodel import db, lm, User
from . import htmlcodes as hcodes

##################################
# If connected to APIs
if BACKEND:

    NODE = 'myapi'
    PORT = 5000
    URL = 'http://%s:%s' % (NODE, PORT)
    API_URL = URL + '/api/'
    LOGIN_URL = API_URL + 'login'
    REGISTER_URL = API_URL + 'register'
    PROFILE_URL = API_URL + 'initprofile'
    HEADERS = {'content-type': 'application/json'}

    @lm.user_loader
    def load_user(id):
        """ How Flask login can choose the current user. """
        return Tokenizer.query.get(id)

    class Tokenizer(db.Model, UserMixin):
        __tablename__ = "tokens"
        id = db.Column(db.Integer, primary_key=True)
        token = db.Column(db.String(255), unique=True, index=True)
        user_id = db.Column(db.Integer)
        authenticated_at = db.Column(db.DateTime)

        def __init__(self, token, user_id):
            self.token = token
            self.user_id = user_id
            self.authenticated_at = datetime.utcnow()

        def __repr__(self):
            return '<Tok for user[%r]> %s' % (self.user_id, self.token)
##################################
# If standalone db/auth/resources
else:
    @lm.user_loader
    def load_user(id):
        """ How Flask login can choose the current user. """
        return User.query.get(int(id))


# lm.login_view = "users.login"

##################################
def register_api(request):
    """ Login requesting token to our API and also store the token """

    # Passwords check
    key1 = 'password'
    key2 = 'password_confirm'
    if key1 not in request or key2 not in request \
       or request[key1] != request[key2]:
        return {'errors': {'passwords mismatch':
                "Passwords provided are not the same"}}, \
                hcodes.HTTP_DEFAULT_SERVICE_FAIL

    # Init
    code = hcodes.HTTP_OK_CREATED
    j = json.dumps(request)
    opts = {'stream': True, 'data': j, 'headers': HEADERS, 'timeout': 5}

    try:

        # Normal registration
        r = requests.post(REGISTER_URL, **opts)
        out = r.json()
        print("Registration out", out)

        if 'errors' in out['response']:
            return out['response'], out['meta']['code']

        # Extra profiling
        opts['data'] = json.dumps({'userid': out['response']['user']['id']})
        r = requests.post(PROFILE_URL, **opts)
        out = r.json()
        print("Profile out", out)

        if 'error' in out['data']:
            return out['data'], out['status']

    except requests.exceptions.ConnectionError:
        return {'errors':
                {'API unavailable': "Cannot connect to APIs server"}}, \
                hcodes.HTTP_DEFAULT_SERVICE_FAIL

    return {'message': 'Registered'}, code


##################################
def login_api(username, password):
    """ Login requesting token to our API and also store the token """

    tokobj = None
    payload = {'email': username, 'password': password}

    try:
        r = requests.post(LOGIN_URL, stream=True,
                          data=json.dumps(payload), headers=HEADERS, timeout=5)
    except requests.exceptions.ConnectionError:
        return {'errors':
                {'API unavailable': "Cannot connect to APIs server"}}, \
                hcodes.HTTP_DEFAULT_SERVICE_FAIL, tokobj
    out = r.json()

    response = {'errors': {'No autorization': "Invalid credentials"}}
    if out['meta']['code'] <= hcodes.HTTP_OK_NORESPONSE:
        data = out['response']['user']
        token = data['authentication_token']

        if token is None or data is None or 'id' not in data:
            return {'errors':
                    {'Misconfiguration': "Backend user not in sync"}}, \
                    hcodes.HTTP_DEFAULT_SERVICE_FAIL, tokobj

        # # Save token inside frontend db
        # registered_user = User.query.filter_by(id=data['id']).first()
        # if registered_user is None:
        #     return {'errors':
        #             {'Misconfiguration': "Backend user not in sync"}}, \
        #             hcodes.HTTP_DEFAULT_SERVICE_FAIL, tokobj
        # tokobj = Tokenizer(token, registered_user.id)

        tokobj = Tokenizer(token, data['id'])

        db.session.add(tokobj)
        db.session.commit()
        response = {'authentication_token': token}

    return response, out['meta']['code'], tokobj


def login_internal(username, password):
    """ Login with internal db """
    registered_user = \
        User.query.filter_by(username=username, password=password).first()

    data = {'errors': {'failed': "No such user/password inside DB"}}
    code = hcodes.HTTP_BAD_UNAUTHORIZED

    if registered_user is not None:
        data = {'user': {'id': registered_user.id}}
# This line above may change
        code = hcodes.HTTP_OK_ACCEPTED

    return data, code, registered_user


def login_point(username, password):
    """ Handle all possible logins """

    # API
    if BACKEND:
        data, code, obj = login_api(username, password)
    # Standalone server
    else:
        data, code, obj = login_internal(username, password)
    # Register positive response to Flask Login in both cases
    if obj is not None:
        login_user(obj)
    # Return (forward) response
    return data, code
