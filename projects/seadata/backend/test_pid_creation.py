# -*- coding: utf-8 -*-

from b2stage.apis.commons.b2handle import PIDgenerator
from restapi.connectors import get_debug_instance
from restapi.connectors.irods import IrodsPythonExt
from restapi.utilities.logs import log

imain = get_debug_instance(IrodsPythonExt)

ifile = ''

log.info("Creating PID Generator")
pmaker = PIDgenerator()
log.info("Requesting PID")
PID = pmaker.pid_request(imain, ifile)
log.info(PID)
