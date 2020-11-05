from datetime import datetime

from b2stage.endpoints.commons import path
from restapi.env import Env
from restapi.exceptions import BadRequest
from restapi.models import Schema, fields
from restapi.utilities.logs import log

seadata_vars = Env.load_group(label="seadata")

# SEADATA_ENABLED = seadata_vars.get('project')
SEADATA_ENABLED = seadata_vars.get("project") == "1"
ORDERS_ENDPOINT = "orders"
EDMO_CODE = seadata_vars.get("edmo_code")
API_VERSION = seadata_vars.get("api_version")


# Validation should raise:
# f"Missing JSON key: {key}
class EndpointsInputSchema(Schema):
    request_id = fields.Str(required=True)
    edmo_code = fields.Int(required=True)
    datetime = fields.Str(required=True)
    api_function = fields.Str(required=True)
    version = fields.Str(required=True)
    test_mode = fields.Str(required=True)

    eudat_backdoor = fields.Bool(required=False, missing=False)

    parameters = fields.Raw(required=True)


class ErrorCodes:
    PID_NOT_FOUND = ("41", "PID not found")
    INGESTION_FILE_NOT_FOUND = ("50", "File requested not found")

    # addzip_restricted_order
    MISSING_ZIPFILENAME_PARAM = ("4000", "Parameter zip_filename is missing")
    MISSING_FILENAME_PARAM = ("4001", "Parameter file_name is missing")
    MISSING_FILESIZE_PARAM = ("4002", "Parameter file_size is missing")
    INVALID_FILESIZE_PARAM = ("4003", "Invalid parameter file_size, integer expected")
    MISSING_FILECOUNT_PARAM = ("4004", "Parameter file_count is missing")
    INVALID_FILECOUNT_PARAM = ("4005", "Invalid parameter file_count, integer expected")
    FILENAME_DOESNT_EXIST = ("4006", "Partner zip (zipfile_name) does not exist")
    CHECKSUM_DOESNT_MATCH = ("4007", "Checksum does not match")
    FILESIZE_DOESNT_MATCH = ("4008", "File size does not match")
    UNZIP_ERROR_FILE_NOT_FOUND = ("4009", "Unzip error: zip file not found")
    UNZIP_ERROR_INVALID_FILE = ("4010", "Unzip error: zip file is invalid")
    UNZIP_ERROR_WRONG_FILECOUNT = ("4011", "Unzip error: file count does not match")
    B2SAFE_UPLOAD_ERROR = ("4012", "Unable to upload restricted zip on b2safe")
    UNZIP_ERROR_INVALID_FILE = ("4013", "Unable to create restricted zip file")
    MISSING_PARTNERS_IDS = ("4014", "Parameter b2access_ids is missing")
    INVALID_B2ACCESS_ID = ("4015", "Invalid b2access id")
    ORDER_NOT_FOUND = ("4016", "Order does not exist or you lack permissions")
    BATCH_NOT_FOUND = ("4017", "Batch does not exist or you lack permissions")
    MISSING_PIDS_LIST = ("4018", "Parameter 'pids' is missing")
    UNABLE_TO_MOVE_IN_PRODUCTION = ("4019", "Cannot move file in production")
    UNABLE_TO_ASSIGN_PID = ("4020", "Unable to assign a PID to the file")
    B2HANDLE_ERROR = ("4021", "PID server (b2handle) unreachable")
    UNABLE_TO_DOWNLOAD_FILE = ("4022", "Unable to download the file")
    ZIP_SPLIT_ERROR = ("4023", "Zip split unexpected error")
    ZIP_SPLIT_ENTRY_TOO_LARGE = (
        "4024",
        "One or more files are larger than max zip size",
    )
    MISSING_BATCHES_PARAMETER = ("4025", "Parameter batches is missing")
    MISSING_ORDERS_PARAMETER = ("4026", "Parameter orders is missing")
    EMPTY_BATCHES_PARAMETER = ("4027", "Parameter batches is empty")
    EMPTY_ORDERS_PARAMETER = ("4028", "Parameter orders is empty")
    MISSING_CHECKSUM_PARAM = ("4029", "Parameter file_checksum is missing")
    INVALID_ZIPFILENAME_PARAM = (
        "4030",
        "Invalid parameter zipfile_name, list expected",
    )
    INVALID_CHECKSUM_PARAM = ("4031", "Invalid parameter file_checksum, list expected")
    INVALID_ZIPFILENAME_LENGTH = ("4032", "Unexpected lenght of zipfile_name parameter")
    INVALID_FILESIZE_LENGTH = ("4033", "Unexpected lenght of file_size parameter")
    INVALID_FILECOUNT_LENGTH = ("4034", "Unexpected lenght of file_count parameter")
    INVALID_CHECKSUM_LENGTH = ("4035", "Unexpected lenght of file_checksum parameter")
    INVALID_FILENAME_PARAM = (
        "4036",
        "Invalid parameter zipfile_name, a string is expected",
    )
    MISSING_BATCH_NUMBER_PARAM = ("4037", "Parameter batch_number is missing")
    UNREACHABLE_DOWNLOAD_PATH = ("4039", "Download path is unreachable")
    MISSING_ORDER_NUMBER_PARAM = ("4040", "Parameter order_number is missing")
    MISSING_DOWNLOAD_PATH_PARAM = ("4041", "Parameter download_path is missing")
    UNABLE_TO_CREATE_ZIP_FILE = ("4042", "Unable to create merged zip file")
    INVALID_ZIP_SPLIT_OUTPUT = ("4043", "Unable to retrieve results from zip split")
    EMPTY_DOWNLOAD_PATH_PARAM = ("4044", "Parameter download_path is empty")
    UNEXPECTED_ERROR = ("4045", "An unexpected error occurred")
    MISSING_REQUEST_ID = ("4046", "Request ID is missing")
    UNABLE_TO_SET_METADATA = ("4047", "Unable to set metadata to the file")


class Metadata:

    """ {
    "cdi_n_code": "1522222",
    "format_n_code": "541555",
    "data_format_l24": "CFPOINT",
    "version": "1"
    } """

    tid = "temp_id"
    keys = [
        "cdi_n_code",
        "format_n_code",
        "data_format_l24",
        "version",
        "batch_date",
        "test_mode",
    ]
    max_size = 10


class ImportManagerAPI:

    _uri = seadata_vars.get("api_im_url")

    def post(self, payload, backdoor=False, edmo_code=None):

        if edmo_code is None:
            edmo_code = EDMO_CODE

        # timestamp '20180320T08:15:44' = YYMMDDTHH:MM:SS
        payload["edmo_code"] = edmo_code
        payload["datetime"] = datetime.today().strftime("%Y%m%dT%H:%M:%S")
        if "api_function" not in payload:
            payload["api_function"] = "unknown_function"
        payload["api_function"] += "_ready"
        payload["version"] = API_VERSION

        if backdoor:
            log.warning(
                "The following json should be sent to ImportManagerAPI, "
                + "but you enabled the backdoor"
            )
            log.info(payload)
            return False

        from restapi.config import PRODUCTION

        if not PRODUCTION:
            log.warning(
                "The following json should be sent to ImportManagerAPI, "
                + "but you are not in production"
            )
            log.info(payload)
            return False

        import requests

        # print("TEST", self._uri)
        r = requests.post(self._uri, json=payload)
        log.info("POST external IM API, status={}, uri={}", r.status_code, self._uri)

        if r.status_code != 200:
            log.error(
                "CDI: failed to call external APIs (status: {}, uri: {})",
                r.status_code,
                self._uri,
            )
            return False
        else:
            log.info(
                "CDI: called POST on external APIs (status: {}, uri: {})",
                r.status_code,
                self._uri,
            )
            return True

        log.warning("Unknown external APIs status")
        return False


# NOTE this function is outside the previous class, and self is passed as parameter
def seadata_pid(self, pid):

    b2handle_output = self.check_pid_content(pid)
    if b2handle_output is None:
        raise BadRequest(f"PID {pid} not found")

    log.verbose("PID {} verified", pid)
    ipath = self.parse_pid_dataobject_path(b2handle_output)
    response = {
        "PID": pid,
        "verified": True,
        "metadata": {},
        "temp_id": path.last_part(ipath),
        "batch_id": path.last_part(path.dir_name(ipath)),
    }

    imain = self.get_main_irods_connection()
    metadata, _ = imain.get_metadata(ipath)

    for key, value in metadata.items():
        if key in Metadata.keys:
            response["metadata"][key] = value

    return response
