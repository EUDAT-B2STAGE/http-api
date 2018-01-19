# -*- coding: utf-8 -*-

"""
Common functions for EUDAT endpoints
"""
from attr import s as AttributedModel, ib as attribute
from restapi.services.detect import detector
from restapi.confs import PRODUCTION, API_URL

from utilities.logs import get_logger

log = get_logger(__name__)

try:
    IRODS_VARS = detector.services_classes.get('irods').variables
except AttributeError:
    IRODS_VARS = {}
IRODS_EXTERNAL = IRODS_VARS.get('external', False)

# CURRENT_B2SAFE_SERVER = 'b2safe.cineca.it'
CURRENT_B2SAFE_SERVER = IRODS_VARS.get('host')
# CURRENT_HTTPAPI_SERVER = 'b2stage-test.cineca.it'
CURRENT_HTTPAPI_SERVER = detector.get_global_var('PROJECT_DOMAIN')

# CURRENT_B2ACCESS_ENVIRONMENT = 'development'
CURRENT_B2ACCESS_ENVIRONMENT = detector.get_global_var('B2ACCESS_ENV')
# CURRENT_MAIN_ENDPOINT = 'registered'
CURRENT_MAIN_ENDPOINT = "%s/%s" \
    % (API_URL, detector.get_global_var('MAIN_ENDPOINT', default=''))
PUBLIC_ENDPOINT = "%s/%s" \
    % (API_URL, detector.get_global_var('PUBLIC_ENDPOINT', default=''))

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
    # Verify certificates or normal credentials
    is_proxy = attribute(default=False)
    valid_credentials = attribute(default=False)
    refreshed = attribute(default=False)
    # Save errors to report
    errors = attribute(default=None)
