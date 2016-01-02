#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
User configuration
"""

import os
import re
import argparse

#################################
# what you could change
STACKTRACE = False
REMOVE_DATA_AT_INIT_TIME = False
USER = 'user@nomail.org'
PWD = 'test'

#############################
# Command line arguments
arg = argparse.ArgumentParser(description='REST API server based on Flask')
arg.add_argument("--no-security", action="store_false", dest='security',
                 help='force removal of login authentication on resources')
arg.add_argument("--debug", action="store_true", dest='debug',
                 help='enable debugging mode')
arg.set_defaults(security=True, debug=False)
args = arg.parse_args()

DEBUG = os.environ.get('API_DEBUG', args.debug)

###################################################
###################################################
SERVER_HOSTS = '0.0.0.0'
SERVER_PORT = int(os.environ.get('PORT', 5000))

# Other configuration files you may use/need inside the 'confs' directory
LOGGING_CONFIG_FILE = 'logging_config.ini'

# Use this to specifiy endpoints based on your resources module
REST_CONFIG_FILE = 'endpoints.ini'

TRAP_BAD_REQUEST_ERRORS = True
PROPAGATE_EXCEPTIONS = False

# Roles
ROLE_ADMIN = 'adminer'
ROLE_USER = 'justauser'

# I am inside the conf dir.
# The base dir is one level up from here
BASE_DIR = re.sub(__package__, '', os.path.abspath(os.path.dirname(__file__)))

#################################
# SQLALCHEMY
BASE_DB_DIR = '/dbs'
SQLLITE_DBFILE = 'backend.db'
dbfile = os.path.join(BASE_DB_DIR, SQLLITE_DBFILE)
SECRET_KEY = 'my-super-secret-keyword_referringtoapiside'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + dbfile
SQLALCHEMY_TRACK_MODIFICATIONS = False

#################################
# SECURITY

# Bug fixing for csrf problem via CURL/token
WTF_CSRF_ENABLED = False
# Force token to last not more than one hour
SECURITY_TOKEN_MAX_AGE = 3600
# Add security to password
# https://pythonhosted.org/Flask-Security/configuration.html
SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
SECURITY_PASSWORD_SALT = "thishastobelongenoughtosayislonglongverylong"

#################################
# ENDPOINTS
ALL_API_URL = '/api'
SECURITY_URL_PREFIX = ALL_API_URL
