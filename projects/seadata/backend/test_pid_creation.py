# -*- coding: utf-8 -*-

from b2stage.apis.commons.b2handle import PIDgenerator
from utilities.logs import get_logger


from restapi.flask_ext import get_debug_instance
from restapi.flask_ext.flask_irods import IrodsPythonExt

log = get_logger(__name__)

imain = get_debug_instance(IrodsPythonExt)

ifile = ''

log.info("Creating PID Generator")
pmaker = PIDgenerator()
log.info("Requesting PID")
PID = pmaker.pid_request(imain, ifile)
log.info(PID)
