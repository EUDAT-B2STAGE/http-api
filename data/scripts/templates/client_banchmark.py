#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example of a simple Python code uploading in parallel all files in ./data/files folder
Warning: Uploaded files are not automatically removed


requirements:
- requests
- rapydo/utils
"""

import os
import threading
import better_exceptions as be
from utilities import helpers
from utilities import apiclient


###########################
# Configuration variables #
###########################

USERNAME = 'someuser'
PASSWORD = 'somepassword'
FILES_PATH = './data/files'
LOG_LEVEL = 'info'  # or 'debug', 'verbose', 'very_verbose'

REMOTE_DOMAIN = 'b2stage-test.cineca.it'  # you may change to another server
REMOTE_HTTPAPI_URI = 'https://%s' % REMOTE_DOMAIN
LOCAL_HTTPAPI_URI = 'http://localhost:8080'

log = apiclient.setup_logger(__name__, level_name=LOG_LEVEL)



def upload(file):
    if not os.path.basename(file_path) in new_dir_content:
        log.info("Uploading file: %s", file_path)
        response = apiclient.call(
            uri, endpoint=apiclient.BASIC_ENDPOINT + new_dir_path,
            token=token, method='put', file=file, timeout=500
        )
        log.info("Uploaded file: %s", file_path)
    else:
        log.warning("%s already exists in %s", file_path, new_dir_path)



if __name__ == '__main__':

    # decide which HTTP API server you should query
    if apiclient.check_cli_arg('remote'):
        uri = REMOTE_HTTPAPI_URI
    else:
        uri = LOCAL_HTTPAPI_URI
    log.very_verbose('init log: %s\nURI [%s]', be, uri)

    ################
    # ACTION: check status
    ################

    # check if HTTP API are alive and/or our connection is working
    apiclient.call(uri)

    ################
    # ACTION: LOGIN
    ################
    # login to HTTP API with B2SAFE credentials
    token, home_path = apiclient.login(uri, USERNAME, PASSWORD)
    # # or set your token from B2ACCESS web login
    # token = 'SOMEHASHSTRINGFROMB2ACCESS'
    # path = '/tempZone/home/YOURUSER'
    log.debug('Home directory is: %s', home_path)
    log.info("Logged in with token: %s...", token[:20])


    # avoid more operations if the user only requested listing
    apiclient.check_cli_arg('list', exit=True)

    # push files found in config dir
    files = apiclient.folder_content(FILES_PATH)
    log.debug("Files to be pushed: %s", files)

    new_dir = 'testing_httpapi'
    # new_dir = helpers.random_name()
    new_dir_path = os.path.join(home_path, new_dir)

    # list current files
    response = apiclient.call(
        uri, endpoint=apiclient.BASIC_ENDPOINT + home_path, token=token)
    home_content = apiclient.parse_irods_listing(response, home_path)
    if len(home_content) < 1 and apiclient.check_cli_arg('list'):
        log.warning("Home directory is empty")

    if new_dir not in home_content:

        ################
        # ACTION: create directory
        ################
        response = apiclient.call(
            uri, endpoint=apiclient.BASIC_ENDPOINT, token=token, method='post',
            payload={'path': new_dir_path}
        )
        log.info("Created directory: %s", response.get('path'))
    else:
        log.warning("Directory already exists: %s", new_dir)

    # list new dir
    new_dir_endpoint = apiclient.BASIC_ENDPOINT + new_dir_path
    response = apiclient.call(uri, endpoint=new_dir_endpoint, token=token)
    new_dir_content = apiclient.parse_irods_listing(response, new_dir_path)

    # upload files in paralle
    threads = []
    for file_path in files:
        t = threading.Thread(target=upload, args=(file_path,))
        threads.append(t)
        t.start()
