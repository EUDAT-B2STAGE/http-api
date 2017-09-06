#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example of a simple Python code interacting with the HTTP API as a client

requirements:
- requests
- rapydo/utils
"""

import os
import sys
import better_exceptions as be
from utilities import helpers
from utilities import apiclient


###########################
# Configuration variables #
###########################

USERNAME = 'muccix'
PASSWORD = 'shortpw'
FILES_PATH = './data/files'
LOG_LEVEL = 'info'  # or 'debug', 'verbose', 'very_verbose'

REMOTE_DOMAIN = 'b2stage.cineca.it'  # you may change to another server
REMOTE_HTTPAPI_URI = 'https://%s' % REMOTE_DOMAIN
LOCAL_HTTPAPI_URI = 'http://localhost:8080'

log = apiclient.setup_logger(__name__, level_name=LOG_LEVEL)

#############
#   MAIN    #
#############


if __name__ == '__main__':

    # decide which HTTP API server you should query
    uri = REMOTE_HTTPAPI_URI
    # uri = LOCAL_HTTPAPI_URI

    ################
    # ACTION: check status
    ################

    # check if HTTP API are alive and/or our connection is working
    apiclient.call(uri)

    ################
    # ACTION: LOGIN
    ################
    # login to HTTP API or set your token from B2ACCESS web login
    token, home_path = apiclient.login(uri, USERNAME, PASSWORD)
    # token = 'SOMEHASHSTRINGFROMB2ACCESS'
    # path = '/tempZone/home/YOURUSER'
    log.very_verbose('init log: %s', be)
    log.debug('Home directory is: %s', home_path)
    log.info("Logged in with token: %s...", token[:20])

    ################
    # ACTION: get directory content
    ################

    # list current files
    response = apiclient.call(
        uri, endpoint=apiclient.BASIC_ENDPOINT + home_path, token=token)
    home_content = apiclient.parse_irods_listing(response, home_path)

    ####################
    # other operations

    # avoid more operations if the user only requested listing
    if len(sys.argv) > 1:
        if '--list' == sys.argv[1]:
            sys.exit(0)

    # push files found in config dir
    files = apiclient.folder_content(FILES_PATH)
    log.debug("Files to be pushed: %s", files)

    new_dir = 'test_http_api'
    new_dir_path = os.path.join(home_path, new_dir)

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

    for file_path in files:

        ################
        # ACTION: upload one file 
        ################
        if not os.path.basename(file_path) in new_dir_content:
            response = apiclient.call(
                uri, endpoint=apiclient.BASIC_ENDPOINT + new_dir_path,
                token=token, method='put', file=file_path
            )
            log.info("Uploaded file: %s", file_path)
        else:
            log.warning("%s already exists in %s", file_path, new_dir_path)

        file_name = file_path

    # list new dir again to see changes
    response = apiclient.call(uri, endpoint=new_dir_endpoint, token=token)
    new_dir_content = apiclient.parse_irods_listing(response, new_dir_path)

    ################
    # ACTION: resolve PID
    ################

    # Get uploaded file metadata
    some_file = helpers.random_element(new_dir_content)
    response = apiclient.call(
        uri, endpoint=os.path.join(new_dir_endpoint, some_file), token=token)
    
    pid = response[0][some_file]['metadata']['PID']
    if pid:
        response = apiclient.call(
        uri, endpoint=os.path.join(apiclient.ADVANCEND_ENDPOINT, pid), token=token)
        log.info("PID resolved with URL: {} and EUDAT/CHECKSUM {}".
                 format(response['URL'], response['EUDAT/CHECKSUM']))
    else:
        log.info("PID not found. PID endpoint skipped")


    ################
    # ACTION: rename one file
    ################

    #some_file = helpers.random_element(new_dir_content)
    new_name = helpers.random_name()

    log.verbose("Random name generated: %s", new_name)
    log.debug("Trying to change '%s' name to '%s'", some_file, new_name)
    response = apiclient.call(
        uri, endpoint=os.path.join(new_dir_endpoint, some_file),
        token=token, method='patch', payload={'newname': new_name}
    )
    log.info("Renamed %s to %s", some_file, new_name)

    # list new dir again to see changes
    response = apiclient.call(uri, endpoint=new_dir_endpoint, token=token)
    new_dir_content = apiclient.parse_irods_listing(response, new_dir_path)


    ################
    # ACTION: delete one file
    ################

    # file_name = next(iter(new_dir_content))
    # file_name = new_dir_content.pop()
    file_name = helpers.random_element(new_dir_content)  # random pop

    response = apiclient.call(
        uri, endpoint=os.path.join(new_dir_endpoint, file_name),
        token=token, method='delete'
    )
    log.info("Deleted: %s", file_name)

    # list new dir again to see changes
    response = apiclient.call(uri, endpoint=new_dir_endpoint, token=token)
    apiclient.parse_irods_listing(response, new_dir_path)


    ################
    # ACTION: delete directory
    ################
    response = apiclient.call(
        uri, endpoint=os.path.join(new_dir_endpoint),
        token=token, method='delete'
    )
    log.info("Deleted directory: %s", new_dir_path)


    ################
    # ACTION: create directory again
    ################
    response = apiclient.call(
        uri, endpoint=apiclient.BASIC_ENDPOINT, token=token, method='post',
        payload={'path': new_dir_path}
    )
    log.info("Created directory: %s", response.get('path'))
