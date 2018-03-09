# -*- coding: utf-8 -*-

"""
B2HANDLE utilities
"""

import os
from b2stage.apis.commons.endpoint import EudatEndpoint
try:
    from b2handle.handleclient \
        import EUDATHandleClient as b2handle
    from b2handle.clientcredentials \
        import PIDClientCredentials as credentials
    from b2handle import handleexceptions
except BaseException:
    b2handle, credentials, handleexceptions = [None] * 3
from utilities import htmlcodes as hcodes
from utilities.logs import get_logger

log = get_logger(__name__)


class B2HandleEndpoint(EudatEndpoint):

    """
    Handling PID requests.
    It includes some methods to connect to B2HANDLE.

    FIXME: it should become a dedicated service in rapydo.
    This way the client could be registered in memory with credentials
    only if the provided credentials are working.
    It should be read only access otherwise.

    """

    eudat_pid_fields = [
        "URL", "EUDAT/CHECKSUM", "EUDAT/UNPUBLISHED",
        "EUDAT/UNPUBLISHED_DATE", "EUDAT/UNPUBLISHED_REASON"
    ]

    eudat_internal_fields = [
        "EUDAT/FIXED_CONTENT", 'PID'
    ]

    def connect_client(self, force_no_credentials=False, disable_logs=False):

        found = False

        if disable_logs:
            import logging
            logging.getLogger('b2handle').setLevel(logging.WARNING)

        # With credentials
        if force_no_credentials:
            client = b2handle.instantiate_for_read_access()
            log.info("PID client connected: NO credentials")
        else:
            file = os.environ.get('HANDLE_CREDENTIALS', None)
            if file is not None:
                from utilities import path
                credentials_path = path.build(file)
                found = path.file_exists_and_nonzero(credentials_path)
                if not found:
                    log.warning(
                        "B2HANDLE credentials file not found %s", file)

            if found:
                client = b2handle.instantiate_with_credentials(
                    credentials.load_from_JSON(file)
                )
                log.info("PID client connected: w/ credentials")
                return client, True

        return client, False

    def check_pid_content(self, pid):
        # from b2handle.handleclient import EUDATHandleClient as b2handle
        # client = b2handle.instantiate_for_read_access()
        client, authenticated = self.connect_client(
            force_no_credentials=True, disable_logs=True)
        return client.retrieve_handle_record(pid)

    def handle_pid_fields(self, client, pid):
        """ Perform B2HANDLE request: retrieve URL from handle """

        import requests
        data = {}
        try:
            for field in self.eudat_pid_fields:
                value = client.get_value_from_handle(pid, field)
                log.info("B2HANDLE: %s=%s", field, value)
                data[field] = value
        except handleexceptions.HandleSyntaxError as e:
            return data, e, hcodes.HTTP_BAD_REQUEST
        except handleexceptions.HandleNotFoundException as e:
            return data, e, hcodes.HTTP_BAD_NOTFOUND
        except handleexceptions.GenericHandleError as e:
            return data, e, hcodes.HTTP_SERVER_ERROR
        except handleexceptions.HandleAuthenticationError as e:
            return data, e, hcodes.HTTP_BAD_UNAUTHORIZED
        except requests.exceptions.ConnectionError as e:
            log.warning("No connection available...")
            return data, e, hcodes.HTTP_SERVER_ERROR
        except BaseException as e:
            log.error("Generic:\n%s(%s)", e.__class__.__name__, e)
            return data, e, hcodes.HTTP_SERVER_ERROR

        return data, None, hcodes.HTTP_FOUND

    def get_pid_metadata(self, pid):

        # First test: check if credentials exists and works
        client, authenticated = self.connect_client()
        data, error, code = self.handle_pid_fields(client, pid)

        # If credentials were found but they gave error
        # TODO: this should be tested at server startup!
        if error is not None and authenticated:
            log.error("B2HANDLE credentials problem: %s", error)
            client, _ = self.connect_client(force_no_credentials=True)
            data, error, code = self.handle_pid_fields(client, pid)

        # Still getting error? Raise any B2HANDLE library problem
        if error is not None:
            log.error("B2HANDLE problem: %s", error)
            return data, \
                self.send_errors(message='B2HANDLE: %s' % error, code=code)
        else:
            return data, None
