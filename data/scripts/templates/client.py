#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example of a simple Python code interacting with the HTTP API as a client

requirements:
- requests
- rapydo/utils
"""

import os
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
remote_calls = apiclient.check_cli_arg('remote')

#############
#   MAIN    #
#############


if __name__ == '__main__':

    # decide which HTTP API server you should query
    if remote_calls:
        from utilities.checks import internet_connection_available
        if not internet_connection_available():
            log.exit("No internet connection")
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

    ################
    # ACTION: get directory content
    ################

    # list current files
    response = apiclient.call(
        uri, endpoint=apiclient.BASIC_ENDPOINT + home_path, token=token)
    home_content = apiclient.parse_irods_listing(response, home_path)
    if len(home_content) < 1 and apiclient.check_cli_arg('list'):
        log.warning("Home directory is empty")

    ####################
    # other operations

    # avoid more operations if the user only requested listing
    apiclient.check_cli_arg('list', exit=True)  # , reverse=True)

    # push files found in config dir
    files = apiclient.folder_content(FILES_PATH)
    log.debug("Files to be pushed: %s", files)

    new_dir = 'testing_httpapi'
    # new_dir = helpers.random_name()
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

            # NOTE: you can wait for the PID registration
            # (assuming the connected B2SAFE is configured so)
            # by adding payload={'pid': True} to the call
            # (probably also a longer timetout, e.g. 20 seconds)

            response = apiclient.call(
                uri,
                endpoint=apiclient.BASIC_ENDPOINT + new_dir_path,
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

    data = response.pop()
    metadata = data.get(some_file, {}).get('metadata', {})
    pid = metadata.get('PID')
    if pid:
        response = apiclient.call(
            uri, token=token,
            endpoint=os.path.join(apiclient.ADVANCEND_ENDPOINT, pid))
        log.info("PID resolved with URL: {} and EUDAT/CHECKSUM {}".
                 format(response['URL'], response['EUDAT/CHECKSUM']))
    else:
        log.info("PID not found. PID endpoint skipped")

    ################
    # ACTION: rename one file
    ################

    # some_file = helpers.random_element(new_dir_content)
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
    new_dir_content = apiclient.parse_irods_listing(response, new_dir_path)

    # avoid cleaning if not requested
    apiclient.check_cli_arg('clean', reverse=True, exit=True)
    log.warning("Cleaning the whole directory for testing: %s", new_dir)

    ################
    # ACTION: delete directory
    ################

    # Remove all files
    for file_name in new_dir_content:
        response = apiclient.call(
            uri, endpoint=os.path.join(new_dir_endpoint, file_name),
            token=token, method='delete'
        )
        log.very_verbose("Cleaning: %s", file_name)

    # Remove the empty directory
    response = apiclient.call(
        uri, endpoint=os.path.join(new_dir_endpoint),
        token=token, method='delete'
    )
    log.info("Deleted directory: %s", new_dir_path)
