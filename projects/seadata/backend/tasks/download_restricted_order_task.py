# -*- coding: utf-8 -*-
import os
import re
import requests
import hashlib
import zipfile
from shutil import rmtree
from plumbum.commands.processes import ProcessExecutionError

from seadata.tasks.seadata import ext_api, celery_app
from seadata.tasks.seadata import MAX_ZIP_SIZE, myorderspath
from seadata.tasks.seadata import notify_error
from seadata.apis.commons.seadatacloud import ErrorCodes

from b2stage.apis.commons import path
from b2stage.apis.commons.basher import BashCommands

from restapi.connectors.celery import send_errors_by_email
from restapi.connectors.irods.client import IrodsException
from restapi.utilities.logs import log


DOWNLOAD_HEADERS = {
    'User-Agent': 'SDC CDI HTTP-APIs',
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate"
}


@celery_app.task(bind=True)
@send_errors_by_email
def download_restricted_order(self, order_id, order_path, myjson):

    with celery_app.app.app_context():

        myjson['parameters']['request_id'] = myjson['request_id']
        myjson['request_id'] = self.request.id

        params = myjson.get('parameters', {})

        backdoor = params.pop('backdoor', False)
        request_edmo_code = myjson.get('edmo_code', None)

        # Make sure you have a path with no trailing slash
        order_path = order_path.rstrip('/')

        try:
            with celery_app.get_service(service='irods') as imain:
                if not imain.is_collection(order_path):
                    return notify_error(
                        ErrorCodes.ORDER_NOT_FOUND,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )

                order_number = params.get("order_number")
                if order_number is None:
                    return notify_error(
                        ErrorCodes.MISSING_ORDER_NUMBER_PARAM,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )

                # check if order_numer == order_id ?

                download_path = params.get("download_path")
                if download_path is None:
                    return notify_error(
                        ErrorCodes.MISSING_DOWNLOAD_PATH_PARAM,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )
                if download_path == '':
                    return notify_error(
                        ErrorCodes.EMPTY_DOWNLOAD_PATH_PARAM,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )

                # NAME OF FINAL ZIP
                filename = params.get('zipfile_name')
                if filename is None:
                    return notify_error(
                        ErrorCodes.MISSING_ZIPFILENAME_PARAM,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )

                base_filename = filename
                if filename.endswith('.zip'):
                    log.warning('{} already contains extention .zip', filename)
                    # TO DO: save base_filename as filename - .zip
                else:
                    filename = path.append_compress_extension(filename)

                final_zip = order_path + '/' + filename.rstrip('/')

                log.info("order_id = {}", order_id)
                log.info("order_path = {}", order_path)
                log.info("final_zip = {}", final_zip)

                # ############################################

                # INPUT PARAMETERS CHECKS

                # zip file uploaded from partner
                file_name = params.get('file_name')
                if file_name is None:
                    return notify_error(
                        ErrorCodes.MISSING_FILENAME_PARAM,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )

                file_size = params.get("file_size")
                if file_size is None:
                    return notify_error(
                        ErrorCodes.MISSING_FILESIZE_PARAM,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )
                try:
                    int(file_size)
                except BaseException:
                    return notify_error(
                        ErrorCodes.INVALID_FILESIZE_PARAM,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )

                file_count = params.get("data_file_count")
                if file_count is None:
                    return notify_error(
                        ErrorCodes.MISSING_FILECOUNT_PARAM,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )
                try:
                    int(file_count)
                except BaseException:
                    return notify_error(
                        ErrorCodes.INVALID_FILECOUNT_PARAM,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )

                file_checksum = params.get("file_checksum")
                if file_checksum is None:
                    return notify_error(
                        ErrorCodes.MISSING_CHECKSUM_PARAM,
                        myjson, backdoor, self,
                        edmo_code=request_edmo_code
                    )

                self.update_state(state="PROGRESS")

                errors = []
                local_finalzip_path = None
                log.info("Merging zip file", file_name)

                if not file_name.endswith('.zip'):
                    file_name = path.append_compress_extension(file_name)

                # 1 - download in local-dir
                download_url = os.path.join(download_path, file_name)
                log.info("Downloading file from {}", download_url)
                try:
                    r = requests.get(
                        download_url,
                        stream=True,
                        verify=False,
                        headers=DOWNLOAD_HEADERS
                    )
                except requests.exceptions.ConnectionError:
                    return notify_error(
                        ErrorCodes.UNREACHABLE_DOWNLOAD_PATH,
                        myjson, backdoor, self,
                        subject=download_url,
                        edmo_code=request_edmo_code
                    )
                except requests.exceptions.MissingSchema as e:
                    log.error(str(e))
                    return notify_error(
                        ErrorCodes.UNREACHABLE_DOWNLOAD_PATH,
                        myjson, backdoor, self,
                        subject=download_url,
                        edmo_code=request_edmo_code
                    )

                if r.status_code != 200:

                    return notify_error(
                        ErrorCodes.UNREACHABLE_DOWNLOAD_PATH,
                        myjson, backdoor, self,
                        subject=download_url,
                        edmo_code=request_edmo_code
                    )

                log.info("Request status = {}", r.status_code)

                local_dir = path.join(myorderspath, order_id)
                path.create(local_dir, directory=True, force=True)
                log.info("Local dir = {}", local_dir)

                local_zip_path = path.join(local_dir, file_name)
                log.info("partial_zip = {}", local_zip_path)

                # from python 3.6
                # with open(local_zip_path, 'wb') as f:
                # up to python 3.5
                with open(str(local_zip_path), 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)

                # 2 - verify checksum
                log.info("Computing checksum for {}...", local_zip_path)
                local_file_checksum = hashlib.md5(
                    open(str(local_zip_path), 'rb').read()
                ).hexdigest()

                if local_file_checksum.lower() != file_checksum.lower():
                    return notify_error(
                        ErrorCodes.CHECKSUM_DOESNT_MATCH,
                        myjson, backdoor, self,
                        subject=file_name,
                        edmo_code=request_edmo_code
                    )
                log.info("File checksum verified for {}", local_zip_path)

                # 3 - verify size
                local_file_size = os.path.getsize(str(local_zip_path))
                if local_file_size != int(file_size):
                    log.error(
                        "File size {} for {}, expected {}",
                        local_file_size, local_zip_path, file_size
                    )
                    return notify_error(
                        ErrorCodes.FILESIZE_DOESNT_MATCH,
                        myjson, backdoor, self,
                        subject=file_name,
                        edmo_code=request_edmo_code
                    )

                log.info("File size verified for {}", local_zip_path)

                # 4 - decompress
                d = os.path.splitext(os.path.basename(str(local_zip_path)))[0]
                local_unzipdir = path.join(local_dir, d)

                if os.path.isdir(str(local_unzipdir)):
                    log.warning("{} already exist, removing it", local_unzipdir)
                    rmtree(str(local_unzipdir), ignore_errors=True)

                path.create(local_dir, directory=True, force=True)
                log.info("Local unzip dir = {}", local_unzipdir)

                log.info("Unzipping {}", local_zip_path)
                zip_ref = None
                try:
                    zip_ref = zipfile.ZipFile(str(local_zip_path), 'r')
                except FileNotFoundError:
                    return notify_error(
                        ErrorCodes.UNZIP_ERROR_FILE_NOT_FOUND,
                        myjson, backdoor, self,
                        subject=file_name,
                        edmo_code=request_edmo_code
                    )

                except zipfile.BadZipFile:
                    return notify_error(
                        ErrorCodes.UNZIP_ERROR_INVALID_FILE,
                        myjson, backdoor, self,
                        subject=file_name,
                        edmo_code=request_edmo_code
                    )

                if zip_ref is not None:
                    zip_ref.extractall(str(local_unzipdir))
                    zip_ref.close()

                # 5 - verify num files?
                local_file_count = 0
                for f in os.listdir(str(local_unzipdir)):
                    local_file_count += 1
                log.info("Unzipped {} files from {}", local_file_count, local_zip_path)

                if local_file_count != int(file_count):
                    log.error("Expected {} files for {}", file_count, local_zip_path)
                    return notify_error(
                        ErrorCodes.UNZIP_ERROR_WRONG_FILECOUNT,
                        myjson, backdoor, self,
                        subject=file_name,
                        edmo_code=request_edmo_code
                    )

                log.info("File count verified for {}", local_zip_path)

                log.info("Verifying final zip: {}", final_zip)
                # 6 - check if final_zip exists
                if not imain.exists(final_zip):
                    # 7 - if not, simply copy partial_zip -> final_zip
                    log.info("Final zip does not exist, copying partial zip")
                    try:
                        imain.put(str(local_zip_path), str(final_zip))
                    except IrodsException as e:
                        log.error(str(e))
                        return notify_error(
                            ErrorCodes.B2SAFE_UPLOAD_ERROR,
                            myjson, backdoor, self,
                            subject=file_name,
                            edmo_code=request_edmo_code
                        )
                    local_finalzip_path = local_zip_path
                else:
                    # 8 - if already exists merge zips
                    log.info("Already exists, merge zip files")

                    log.info("Copying zipfile locally")
                    local_finalzip_path = path.join(
                        local_dir, os.path.basename(str(final_zip)))
                    imain.open(str(final_zip), str(local_finalzip_path))

                    log.info("Reading local zipfile")
                    zip_ref = None
                    try:
                        zip_ref = zipfile.ZipFile(str(local_finalzip_path), 'a')
                    except FileNotFoundError:
                        log.error("Local file not found: {}", local_finalzip_path)
                        return notify_error(
                            ErrorCodes.UNZIP_ERROR_FILE_NOT_FOUND,
                            myjson, backdoor, self,
                            subject=final_zip,
                            edmo_code=request_edmo_code
                        )

                    except zipfile.BadZipFile:
                        log.error("Invalid local file: {}", local_finalzip_path)
                        return notify_error(
                            ErrorCodes.UNZIP_ERROR_INVALID_FILE,
                            myjson, backdoor, self,
                            subject=final_zip,
                            edmo_code=request_edmo_code
                        )

                    log.info("Adding files to local zipfile")
                    if zip_ref is not None:
                        try:
                            for f in os.listdir(str(local_unzipdir)):
                                # log.debug("Adding {}", f)
                                zip_ref.write(
                                    os.path.join(str(local_unzipdir), f), f)
                            zip_ref.close()
                        except BaseException as e:
                            log.error(e)
                            return notify_error(
                                ErrorCodes.UNABLE_TO_CREATE_ZIP_FILE,
                                myjson, backdoor, self,
                                subject=final_zip,
                                edmo_code=request_edmo_code
                            )

                    log.info("Creating a backup copy of final zip")
                    backup_zip = final_zip + ".bak"
                    if imain.is_dataobject(backup_zip):
                        log.info(
                            "{} already exists, removing previous backup",
                            backup_zip
                        )
                        imain.remove(backup_zip)
                    imain.move(final_zip, backup_zip)

                    log.info("Uploading final updated zip")
                    imain.put(str(local_finalzip_path), str(final_zip))

                    # imain.remove(local_zip_path)
                rmtree(str(local_unzipdir), ignore_errors=True)

                self.update_state(state="COMPLETED")

                if local_finalzip_path is None:
                    log.warning(
                        "Local_finalzip_path is None, unable to check size of file zip"
                    )
                elif os.path.getsize(str(local_finalzip_path)) > MAX_ZIP_SIZE:
                    log.warning("Zip too large, splitting {}", local_finalzip_path)

                    # Create a sub folder for split files. If already exists,
                    # remove it before to start from a clean environment
                    split_path = path.join(local_dir, "restricted_zip_split")
                    # split_path is an object
                    rmtree(str(split_path), ignore_errors=True)
                    # path create requires a path object
                    path.create(split_path, directory=True, force=True)
                    # path object is no longer required, cast to string
                    split_path = str(split_path)

                    # Execute the split of the whole zip
                    bash = BashCommands()
                    split_params = [
                        '-n', MAX_ZIP_SIZE,
                        '-b', split_path,
                        local_finalzip_path
                    ]
                    try:
                        bash.execute_command('/usr/bin/zipsplit', split_params)
                    except ProcessExecutionError as e:

                        if 'Entry is larger than max split size' in e.stdout:
                            reg = 'Entry too big to split, read, or write \((.*)\)'
                            extra = None
                            m = re.search(reg, e.stdout)
                            if m:
                                extra = m.group(1)
                            return notify_error(
                                ErrorCodes.ZIP_SPLIT_ENTRY_TOO_LARGE,
                                myjson, backdoor, self, extra=extra,
                                edmo_code=request_edmo_code
                            )
                        else:
                            log.error(e.stdout)

                        return notify_error(
                            ErrorCodes.ZIP_SPLIT_ERROR,
                            myjson, backdoor, self, extra=str(local_finalzip_path),
                            edmo_code=request_edmo_code
                        )

                    regexp = '^.*[^0-9]([0-9]+).zip$'
                    zip_files = os.listdir(split_path)
                    for subzip_file in zip_files:
                        m = re.search(regexp, subzip_file)
                        if not m:
                            log.error(
                                "Cannot extract index from zip name: {}",
                                subzip_file
                            )
                            return notify_error(
                                ErrorCodes.INVALID_ZIP_SPLIT_OUTPUT,
                                myjson, backdoor, self, extra=str(local_finalzip_path)
                            )
                        index = m.group(1).lstrip('0')
                        subzip_path = path.join(split_path, subzip_file)

                        subzip_ifile = path.append_compress_extension(
                            "{}{}".format(base_filename, index)
                        )
                        subzip_ipath = path.join(order_path, subzip_ifile)

                        log.info("Uploading {} -> {}", subzip_path, subzip_ipath)
                        imain.put(str(subzip_path), str(subzip_ipath))

                if len(errors) > 0:
                    myjson['errors'] = errors

                ret = ext_api.post(
                    myjson,
                    backdoor=backdoor,
                    edmo_code=request_edmo_code
                )
                log.info('CDI IM CALL = {}', ret)
                return "COMPLETED"
        except BaseException as e:
            log.error(e)
            log.error(type(e))
            return notify_error(
                ErrorCodes.UNEXPECTED_ERROR,
                myjson, backdoor, self
            )
