# -*- coding: utf-8 -*-

""" Main routes """

import requests
import json
# import commentjson as json
# from datetime import datetime
# from flask import Response, stream_with_context
# from flask.ext.login import login_user, UserMixin
# from .basemodel import db, lm, User
from . import htmlcodes as hcodes

from config import API_URL, get_logger
logger = get_logger(__name__)

##################################
# If connected to APIs

##// TO FIX!!
LOGIN_URL = API_URL + 'logintest'
# LOGIN_URL = API_URL + 'login'

REGISTER_URL = API_URL + 'register'
PROFILE_URL = API_URL + 'initprofile'
HEADERS = {'content-type': 'application/json'}


"""
Not going to be called.
Because we will not use any endpoint on the frontend side
which will require the user to be logged.

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

@lm.user_loader
def load_user(id):
    return Tokenizer.query.get(id)
"""


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

    # Info check
    key1 = 'name'
    key2 = 'surname'
    if key1 not in request \
       or request[key1] is None \
       or key2 not in request \
       or request[key2] is None:
        return {'errors': {'information required':
                "No profile info: name and/or surname"}}, \
            hcodes.HTTP_DEFAULT_SERVICE_FAIL

    # Init
    code = hcodes.HTTP_OK_CREATED
    j = json.dumps(request)
    opts = {'stream': True, 'data': j, 'headers': HEADERS, 'timeout': 5}

    try:

        # Normal registration
        r = requests.post(REGISTER_URL, **opts)
        out = r.json()
        logger.debug("Registration step 1 [%s]" % out)
        if 'errors' in out['response']:
            return out['response'], out['meta']['code']

        # Extra profiling
        request['userid'] = out['response']['user']['id']
        opts['data'] = json.dumps(request)
        r = requests.post(PROFILE_URL, **opts)
        out = r.json()
        logger.debug("Registration step 2 [%s]" % out)
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

    user_object = None
    payload = {'username': username, 'password': password}

    try:
        r = requests.post(LOGIN_URL, stream=True,
                          data=json.dumps(payload), headers=HEADERS, timeout=5)
    except requests.exceptions.ConnectionError:
        return {'errors':
                {'API unavailable': "Cannot connect to APIs server"}}, \
            hcodes.HTTP_DEFAULT_SERVICE_FAIL, user_object
    out = r.json()

    response = {'errors': {'No autorization': "Invalid credentials"}}

    # If wanting to check errors
    if 'Response' in out and 'errors' in out['Response']:
        errors = out['Response']['errors']

        # Search for known errors
        if errors is not None:
            if 'email' in errors:
                for error in errors['email']:
                    if 'confirmation' in error:
                        logger.info(
                            "Registered user, waiting for approval: %s"
                            % username)
                        err = {error:
                               'This account has not yet been approved ...'}
                        response['errors'] = err
            else:
                response['errors'] = out['Response']['errors']

    # Positive response
    if 'Meta' in out and out['Meta']['status'] <= hcodes.HTTP_OK_NORESPONSE:

        # data = out['Response']['user']
        # token = data['authentication_token']

        # if token is None or data is None or 'id' not in data:
        if 'Authentication-token' not in out['Response']['data']:
            return {'errors':
                    {'Misconfiguration': "Backend token is invalid"}}, \
                hcodes.HTTP_DEFAULT_SERVICE_FAIL, user_object

        # Get the JWT token
        token = out['Response']['data']['Authentication-token']

        #########################
        # JWT STUFF
        JWT_SECRET = 'secret'
        JWT_ALGO = 'HS256'
        import jwt
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        print("TOKEN PAYLOAD", payload)
        #########################

        ####################################
        # Save token inside frontend db ?
            # USELESS NOW
        # tokobj = Tokenizer(token, data['id'])
        # db.session.add(tokobj)
        # db.session.commit()

        # Needed by angularjs satellizer
        response = {'authentication_token': token}

        # Register positive response to Flask Login in both cases
        #login_user(user_object)

    return response, out['Meta']['status']
