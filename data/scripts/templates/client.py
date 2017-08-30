#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example of a simple Python code interacting with the HTTP API as a client

requirements:
- requests
- rapydo/utils
"""


###########################
# Configuration variables #
###########################

USERNAME = 'someuser'
PASSWORD = 'yourpassword'

LOG_LEVEL = 'info'  # or 'debug', 'verbose', 'very_verbose'
# LOG_LEVEL = 'very_verbose'
FILES_PATH = './data/files'

LOCAL_HTTPAPI_URI = 'http://localhost:8080'
REMOTE_DOMAIN = 'b2stage.cineca.it'  # you may change here
REMOTE_HTTPAPI_URI = 'https://%s' % REMOTE_DOMAIN
LOGIN_ENDPOINT = '/auth/b2safeproxy'
BASIC_ENDPOINT = '/api/registered'
ADVANCEND_ENDPOINT = '/api/pids'


#####################
# Helpers functions #
#####################

def setup_logger():

    from utilities.logs import get_logger, logging, set_global_log_level
    log_level = getattr(logging, LOG_LEVEL.upper())
    set_global_log_level(package=__package__, app_level=log_level)
    return get_logger(__name__)

    # ## or If you do not want a dependency to rapydo/utils:

    # import logging
    # logger = logging.getLogger(__name__)
    # handler = logging.StreamHandler()
    # formatter = logging.Formatter(
    #     '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)
    # logger.setLevel(logging.DEBUG)
    # return logger


log = setup_logger()


def parse_api_output(req):

    content = None
    failed = False
    output_key = 'Response'
    output_content = 'data'
    output_errors = 'errors'

    response = req.json()

    if req.status_code > 299:
        log.critical("API request failed (or not completed)")
        failed = True

    # log.pp(response)  # DEBUG
    if output_key in response:
        output = response[output_key]
        errors = output.get(output_errors, [])
        if errors is not None and len(errors) > 0:
            for error in errors:
                log.error(error)
        content = output.get(output_content)

    if failed:
        log.exit()
    else:
        return content


def call_api(uri, endpoint=None, method='get', payload=None, token=None):

    if endpoint is None:
        endpoint = '/api/status'
    headers = {'content-type': 'application/json'}
    if token is not None:
        headers['Authorization'] = "Bearer %s" % token

    import requests
    requests_callable = getattr(requests, method)

    if method == 'post':
        import json
        payload = json.dumps(payload)

    log.very_verbose('Calling %s on %s' % (method, endpoint))
    request = requests_callable(
        uri + endpoint,
        headers=headers, timeout=10, data=payload)
    log.very_verbose(request.url)

    out = parse_api_output(request)
    log.verbose("HTTP-API CALL[%s]: %s" % (method.upper(), out))

    return out


def login_api(uri, username, password):
    out = call_api(
        uri, method='post', endpoint=LOGIN_ENDPOINT,
        payload={'username': username, 'password': password}
    )
    log.debug("Current iRODS user: %s" % out.get('b2safe_user'))
    return out.get('token'), out.get('b2safe_home')


def folder_content(folder_path):
    import os
    if not os.path.exists(folder_path):
        log.exit("%s does not exist" % folder_path)

    import glob
    log.debug("Looking for directory '%s'" % FILES_PATH)
    files = glob.glob(os.path.join(FILES_PATH, "*"))
    if len(files) < 1:
        log.exit("%s does not contain any file" % folder_path)

    return files


def stream_file(file_path):
    with open(file_path, encoding='utf-8') as f:
        print(f)


#############
#   MAIN    #
#############

if __name__ == '__main__':

    # decide which HTTP API server you should query
    uri = REMOTE_HTTPAPI_URI
    # uri = LOCAL_HTTPAPI_URI

    # check if HTTP API are alive and/or our connection is working
    call_api(uri)

    # login to HTTP API or set your token from B2ACCESS web login
    token, home_path = login_api(uri, USERNAME, PASSWORD)
    # token = 'SOMEHASHSTRINGFROMB2ACCESS'
    # path = '/tempZone/home/YOURUSER'
    log.debug('Home directory is: %s' % home_path)
    log.info("Logged in with token: %s..." % token[:20])

    # list current files
    endpoint = BASIC_ENDPOINT + home_path
    content = call_api(uri, endpoint=endpoint, token=token)
    log.info("Home directory content:")
    log.pp(content)

    ####################
    # other operations

    # avoid more operations if only listing
    import sys
    if len(sys.argv) > 1:
        if '--list' == sys.argv[1]:
            sys.exit(0)

    # push files
    for file in folder_content(FILES_PATH):
        print(file)
