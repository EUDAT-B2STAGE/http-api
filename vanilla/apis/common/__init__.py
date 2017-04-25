# -*- coding: utf-8 -*-

"""
Common functions for EUDAT endpoints
"""
from attr import s as AttributedModel, ib as attribute
from rapydo.services.detect import detector
from rapydo.confs import PRODUCTION

from rapydo.utils.logs import get_logger

log = get_logger(__name__)

IRODS_VARS = detector.services_classes.get('irods').variables

CURRENT_B2SAFE_SERVER = IRODS_VARS.get('host')
# CURRENT_B2SAFE_SERVER = 'b2safe.cineca.it'
# TO FIX: this is DOMAIN in os/detect
CURRENT_HTTPAPI_SERVER = detector.get_global_var('PROJECT_DOMAIN')
# CURRENT_HTTPAPI_SERVER = 'b2stage.cineca.it'

IRODS_PROTOCOL = 'irods'

HTTP_PROTOCOL = 'http'
if PRODUCTION:
    HTTP_PROTOCOL = 'https'


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
    # Save errors to report
    errors = attribute(default=None)
