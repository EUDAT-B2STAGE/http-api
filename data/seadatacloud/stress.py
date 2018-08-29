# -*- coding: utf-8 -*-

#################################
import sys
import random
from datetime import datetime
import better_exceptions as be
# from utilities import helpers
from utilities import apiclient

#################################
REMOTE_DOMAIN = 'seadata.cineca.it'
URI = 'https://%s' % REMOTE_DOMAIN
USERNAME = 'stresstest'
PASSWORD = 'somepassword'
# LOG_LEVEL = 'info'  # or 'debug', 'verbose', 'very_verbose'
LOG_LEVEL = 'verbose'

#################################
log = apiclient.setup_logger(__name__, level_name=LOG_LEVEL)
log.very_verbose('init log: %s\nURI [%s]', be, URI)
# apiclient.call(URI)

#################################
# log.pp(sys.argv)
order_size = 100
if len(sys.argv) > 1:
    order_size = int(sys.argv[1])
log.debug("Order size: %s", order_size)

#################################
# read json
with open('init.json') as f:
    import json
    myjson = json.load(f)
    log.info("Total PIDs: %s", len(myjson))

#################################
pids = random.sample(list(myjson.values()), order_size)
# log.pp(pids)

#################################
# login to HTTP API with B2SAFE credentials
token, _ = apiclient.login(URI, USERNAME, PASSWORD)
log.info("Logged in with token: %s...", token[:20])

# #################################
# pass
order_id = 'pythonpaulie_00%s' % datetime.today().strftime("%H%M%S")
now = datetime.today().strftime("%Y%m%dT%H:%M:%S")
endpoint = '/api/orders'
params = {
    "request_id": order_id, "edmo_code": 12345, "datetime": now,
    "version": "1", "api_function": "order_create_zipfile",
    "test_mode": "true", "parameters": {
        "login_code": "unknown", "restricted": "false",
        "file_name": "order_%s_unrestricted" % order_id,
        "order_number": order_id, "pids": pids, "file_count": len(pids),
    }
}
# log.pp(params)
apiclient.call(
    URI, method='post', endpoint=endpoint,
    token=token, payload=params
)
# log.pp(res)
