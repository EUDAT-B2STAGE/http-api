# -*- coding: utf-8 -*-

""" Configurations """

import os
import logging
from logging.config import fileConfig
# import json
import commentjson as json

#######################
# Warning: this decides about final configuration
DEBUG = True
PATH = 'angular'   # Main directory where all conf files are found
# Warning: this decides about final configuration
#######################

CONFIG_PATH = 'config'
JSON_EXT = 'json'
FRAMEWORKS = ['bootstrap', 'materialize', 'foundation']

BACKEND = False
for key in os.environ.keys():
    if 'myapi' == key.lower()[0:5]:
        BACKEND = True


########################################


########################################
# Read user config
def read_files(path):
    """ All user specifications """
    sections = [
        # Basic options
        'content', 'models', 'options',
        # Framework specific and user custom files
        'frameworks',
        # Choose the blueprint to work with
        'blueprints/js_init',
        ]
    myjson = {}
    for section in sections:
        filename = os.path.join(CONFIG_PATH, path, section + "." + JSON_EXT)
        with open(filename) as f:
            name = section.split('/')[0]
            myjson[name] = json.load(f)
        # if section == 'frameworks':
        #     print(myjson[section])
    return myjson

# Use the function
user_config = read_files(PATH)


########################################
class BaseConfig(object):

    DEBUG = os.environ.get('APP_DEBUG', DEBUG)
    TESTING = False
    MYCONFIG_PATH = os.path.join(CONFIG_PATH, PATH)
    BASE_DB_DIR = '/dbs'
    SQLLITE_DBFILE = 'frontend.db'
    dbfile = os.path.join(BASE_DB_DIR, SQLLITE_DBFILE)
    SECRET_KEY = 'my-super-secret-keyword_referringtofrontendside'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + dbfile
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my precious'

    HOST = 'localhost'
    PORT = int(os.environ.get('PORT', 5000))

    BASIC_USER = {
        'username': user_config['content'].get('username', 'prototype'),
        'password': user_config['content'].get('password', 'test'),
        'email': user_config['content'].get('email', 'idonotexist@test.com')
    }

########################################
# LOGGING
if BaseConfig.DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO
# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

# Start with null handler
logging.getLogger(__name__).addHandler(NullHandler())
# Read format and other things from file configuration
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
fileConfig(os.path.join(CURRENT_DIR, 'logging.ini'))


def get_logger(name):
    """ Recover the right logger + set a proper specific level """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    return logger


def silence_loggers():
    root_logger = logging.getLogger()
    first = True
    for handler in root_logger.handlers:
        print("HANDLER", handler)
        if first:
            first = False
            continue
        root_logger.removeHandler(handler)
