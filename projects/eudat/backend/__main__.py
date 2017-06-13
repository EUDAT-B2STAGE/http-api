#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

RESTful API Python 3 Flask server

"""

import os
import better_exceptions as be
from rapydo.confs import PRODUCTION
from rapydo.utils.logs import get_logger
from rapydo.server import create_app

log = get_logger(__name__)

# Connection is HTTP internally to containers; proxy will handle HTTPS calls.
# We can safely disable HTTPS on OAUTHLIB requests
if PRODUCTION:
    # http://stackoverflow.com/a/27785830/2114395
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

#############################
# BE FLASK
app = create_app(name='REST_API')

if __name__ == "__main__":
    log.debug("Server running (w/ %s)" % be.__name__)

    # NOTE: 'threaded' option avoid to see
    # angular request on this server dropping
    # and becoming slow if not totally frozen
    app.run(host='0.0.0.0', threaded=True)