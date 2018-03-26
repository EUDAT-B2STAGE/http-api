# -*- coding: utf-8 -*-

from restapi.services.detect import detector
from utilities.logs import get_logger

log = get_logger(__name__)
seadata_vars = detector.load_group(label='seadata')

SEADATA_ENABLED = seadata_vars.get('project')
ORDERS_ENDPOINT = 'orders'


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

        import requests
        # print("TEST", self._uri)
        r = requests.post(self._uri, data=payload)
        log.info("Called POST on external APIs: %s", r.status_code)
