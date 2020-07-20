from b2stage.apis.commons.b2handle import PIDgenerator
from b2stage.connectors.irods import IrodsPythonExt
from restapi.connectors import get_debug_instance
from restapi.utilities.logs import log

imain = get_debug_instance(IrodsPythonExt)

ifile = ""

log.info("Creating PID Generator")
pmaker = PIDgenerator()
log.info("Requesting PID")
PID = pmaker.pid_request(imain, ifile)
log.info(PID)
