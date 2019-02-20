# -*- coding: utf-8 -*-

from b2stage.apis.commons.b2handle import PIDgenerator


from restapi.flask_ext import get_debug_instance
from restapi.flask_ext.flask_irods import IrodsPythonExt
imain = get_debug_instance(IrodsPythonExt)

ifile = ''

pmaker = PIDgenerator()
PID = pmaker.pid_request(imain, ifile)
print(PID)
