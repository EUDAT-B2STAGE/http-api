# -*- coding: utf-8 -*-

from datetime import datetime
from restapi.services.detect import detector
from utilities.logs import get_logger

log = get_logger(__name__)
seadata_vars = detector.load_group(label='seadata')

# SEADATA_ENABLED = seadata_vars.get('project')
SEADATA_ENABLED = seadata_vars.get('project') == '1'
ORDERS_ENDPOINT = 'orders'
EDMO_CODE = seadata_vars.get('edmo_code')


class ErrorCodes(object):
    PID_NOT_FOUND = ("41", "PID not found")
    INGESTION_FILE_NOT_FOUND = ("50", "File requested not found")
    INTERNAL_SERVER_ERROR = ("54", "Internal error, restart your request")

    # addzip_restricted_order
    MISSING_ZIPFILENAME_PARAM = ("4000", "Parameter zipfile_name is missing")
    MISSING_FILENAME_PARAM = ("4001", "Parameter file_name is missing")
    MISSING_FILESIZE_PARAM = ("4002", "Parameter file_size is missing")
    INVALID_FILESIZE_PARAM = ("4003", "Invalid parameter file_size")
    MISSING_FILECOUNT_PARAM = ("4004", "Parameter file_count is missing")
    INVALID_FILECOUNT_PARAM = ("4005", "Invalid parameter file_count")
    FILENAME_DOESNT_EXIST = ("4006", "Partner zip (file_name) does not exist")
    CHECKSUM_DOESNT_MATCH = ("4007", "Checksum does not match")
    FILESIZE_DOESNT_MATCH = ("4008", "File size does not match")
    UNZIP_ERROR_FILE_NOT_FOUND = ("4009", "Unzip error: partner zip not found")
    UNZIP_ERROR_INVALID_FILE = ("4010", "Unzip error: partner zip is invalid")
    UNZIP_ERROR_WRONG_FILECOUNT = ("4011", "Unzip error: file count does not match")
    B2SAFE_UPLOAD_ERROR = ("4012", "Unable to upload restricted zip on b2safe")


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

    def post(self, payload, instance=None):

        from restapi.confs import PRODUCTION
        if not PRODUCTION:
            log.debug("Skipping ImportManagerAPI")
            return False

        if instance is not None:
            instance_id = str(id(instance))
            payload['request_id'] = instance_id
        # timestamp '20180320T08:15:44' = YYMMDDTHH:MM:SS
        payload['edmo_code'] = EDMO_CODE
        payload['datetime'] = datetime.today().strftime("%Y%m%dT%H:%M:%S")
        payload['api_function'] += '_ready'

        import requests
        # print("TEST", self._uri)
        r = requests.post(self._uri, json=payload)

        from utilities import htmlcodes as hcodes
        if r.status_code != hcodes.HTTP_OK_BASIC:
            log.error(
                "CDI: failed to call external APIs (status: %s)",
                r.status_code)
            return False
        else:
            log.info(
                "CDI: called POST on external APIs (status: %s)",
                r.status_code)
            return True
