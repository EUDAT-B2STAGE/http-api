# -*- coding: utf-8 -*-

from restapi.services.detect import detector
SEADATA_ENABLED = detector.get_global_var('SEADATA_PROJECT')
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
