"""
Common functions for EUDAT endpoints
"""
from attr import ib as attribute
from attr import s as AttributedModel
from restapi.config import API_URL, PRODUCTION
from restapi.env import Env

# from restapi.utilities.logs import log

try:
    IRODS_VARS = Env.load_variables_group(prefix="irods")
except AttributeError:
    IRODS_VARS = {}
# IRODS_EXTERNAL = IRODS_VARS.get("external", False)

CURRENT_B2SAFE_SERVER = IRODS_VARS.get("host")
CURRENT_HTTPAPI_SERVER = Env.get("DOMAIN")
CURRENT_B2ACCESS_ENVIRONMENT = Env.get("B2ACCESS_ENV")

MAIN_ENDPOINT_NAME = Env.get("MAIN_ENDPOINT", default="")
PUBLIC_ENDPOINT_NAME = Env.get("PUBLIC_ENDPOINT", default="")

CURRENT_MAIN_ENDPOINT = f"{API_URL}/{MAIN_ENDPOINT_NAME}"
PUBLIC_ENDPOINT = f"{API_URL}/{PUBLIC_ENDPOINT_NAME}"

IRODS_PROTOCOL = "irods"

HTTP_PROTOCOL = "http"
if PRODUCTION:
    HTTP_PROTOCOL = "https"
else:
    # FIXME: how to get the PORT?
    CURRENT_HTTPAPI_SERVER += ":8080"


########################
#  A class with attributes
########################
@AttributedModel
class InitObj:
    """
    A pythonic way to handle a method response with different features.
    Here's the list of needed attributes:
    """

    # User info
    username = attribute(default=None)
    # extuser_object = attribute(default=None)
    # Service handlers
    icommands = attribute(default=None)
    # db_handler = attribute(default=None)
    valid_credentials = attribute(default=False)
    refreshed = attribute(default=False)
    # Save errors to report
    errors = attribute(default=None)
