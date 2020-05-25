# -*- coding: utf-8 -*-

"""
Common functions for EUDAT endpoints
"""
from attr import s as AttributedModel, ib as attribute
from restapi.services.detect import detector
from restapi.confs import PRODUCTION, API_URL

# from restapi.utilities.logs import log

try:
    IRODS_VARS = detector.load_variables(prefix='irods')
except AttributeError:
    IRODS_VARS = {}
IRODS_EXTERNAL = IRODS_VARS.get('external', False)

CURRENT_B2SAFE_SERVER = IRODS_VARS.get('host')
CURRENT_HTTPAPI_SERVER = detector.get_global_var('DOMAIN')
CURRENT_B2ACCESS_ENVIRONMENT = detector.get_global_var('B2ACCESS_ENV')

MAIN_ENDPOINT_NAME = detector.get_global_var('MAIN_ENDPOINT', default='')
PUBLIC_ENDPOINT_NAME = detector.get_global_var('PUBLIC_ENDPOINT', default='')

CURRENT_MAIN_ENDPOINT = "{}/{}".format(API_URL, MAIN_ENDPOINT_NAME)
PUBLIC_ENDPOINT = "{}/{}".format(API_URL, PUBLIC_ENDPOINT_NAME)

IRODS_PROTOCOL = 'irods'

HTTP_PROTOCOL = 'http'
if PRODUCTION:
    HTTP_PROTOCOL = 'https'
else:
    # FIXME: how to get the PORT?
    CURRENT_HTTPAPI_SERVER += ":8080"


########################
#  A class with attributes
########################
@AttributedModel
class InitObj(object):
    """
    A pythonic way to handle a method response with different features.
    Here's the list of needed attributes:
    """

    # User info
    username = attribute(default=None)
    extuser_object = attribute(default=None)
    # Service handlers
    icommands = attribute(default=None)
    db_handler = attribute(default=None)
    valid_credentials = attribute(default=False)
    refreshed = attribute(default=False)
    # Save errors to report
    errors = attribute(default=None)
