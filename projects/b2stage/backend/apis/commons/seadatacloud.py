# -*- coding: utf-8 -*-

from datetime import datetime
from restapi.services.detect import detector
from utilities.logs import get_logger

log = get_logger(__name__)
seadata_vars = detector.load_group(label='seadata')

# SEADATA_ENABLED = seadata_vars.get('project')
SEADATA_ENABLED = seadata_vars.get('project') == '1'
ORDERS_ENDPOINT = 'orders'


class ErrorCodes(object):

    PID_NOT_FOUND = "41"
    INGESTION_FILE_NOT_FOUND = "50"


class Metadata(object):

    """ {
    "cdi_n_code": "1522222",
    "format_n_code": "541555",
    "data_format_l24": "CFPOINT",
    "version": "1"
    } """

    tid = 'temp_id'
    keys = [
        "cdi_n_code", "format_n_code", "data_format_l24", "version",
    ]
    max_size = 10


class ImportManagerAPI(object):

    _uri = seadata_vars.get('api_im_url')

    def post(self, payload):

        from restapi.confs import PRODUCTION
        if not PRODUCTION:
            log.debug("Skipping ImportManagerAPI")
            return False

        # timestamp '20180320T08:15:44' = YYMMDDTHH:MM:SS
        payload['datetime'] = datetime.today().strftime("%Y%m%dT%H:%M:%S")
        payload['api_function'] += '_ready'

        import requests
        # print("TEST", self._uri)
        r = requests.post(self._uri, json=payload)

        from utilities import htmlcodes as hcodes
        if r.status_code != hcodes.HTTP_OK_BASIC:
            log.error("Failed to call external APIs: %s", r.status_code)
            return False
        else:
            log.info("Called POST on external APIs: %s", r.status_code)
            return True
