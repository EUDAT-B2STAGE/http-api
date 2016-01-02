#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import pkg_resources
try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'
from logging.config import fileConfig
from confs.config import LOGGING_CONFIG_FILE, REST_CONFIG_FILE, DEBUG

myself = "Paolo D'Onorio De Meo <p.donoriodemeo@gmail.com>"
lic = "MIT"

################
# From the directory where the app is launched
PROJECT_DIR = '.'
CONFIG_DIR = 'confs'
LOG_CONFIG = os.path.join(PROJECT_DIR, CONFIG_DIR, LOGGING_CONFIG_FILE)
REST_CONFIG = os.path.join(PROJECT_DIR, CONFIG_DIR, REST_CONFIG_FILE)

################
# LOGGING
if DEBUG:
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

logging.getLogger(__name__).addHandler(NullHandler())
# Read format and other things from file configuration
fileConfig(LOG_CONFIG)


def get_logger(name):
    """ Recover the right logger + set a proper specific level """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    return logger


# # Does not work very well
# def silence_loggers(new_level=logging.ERROR):
#     """ Shut down log from other apps """

#     if '.' not in __package__:
#         name = __package__
#     else:
#         end = __package__.find('.')
#         name = __package__[:end]

#     from jinja2._compat import iteritems
#     for key, value in iteritems(logging.Logger.manager.loggerDict):
#         if isinstance(value, logging.Logger) and \
#          not key.startswith(name + '.') and \
#          not key.startswith(name):
#             print(key, value)
#             value.setLevel(new_level)

def silence_loggers():
    root_logger = logging.getLogger()
    first = True
    for handler in root_logger.handlers:
        if first:
            first = False
            continue
        root_logger.removeHandler(handler)
        #handler.close()
