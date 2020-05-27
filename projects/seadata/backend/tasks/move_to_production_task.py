# -*- coding: utf-8 -*-
import os
import time

from seadata.tasks.seadata import ext_api, celery_app, r
from seadata.tasks.seadata import notify_error
from seadata.apis.commons.seadatacloud import ErrorCodes
from seadata.apis.commons.seadatacloud import Metadata as md
from seadata.apis.commons.queue import prepare_message

from b2stage.apis.commons import path
from b2stage.apis.commons.b2handle import PIDgenerator

from restapi.connectors.celery import send_errors_by_email
from restapi.utilities.logs import log

pmaker = PIDgenerator()


@celery_app.task(bind=True)
@send_errors_by_email
def move_to_production_task(self, batch_id, batch_path, cloud_path, myjson):

    with celery_app.app.app_context():

        self.update_state(
            state="STARTING", meta={'total': None, 'step': 0, 'errors': 0})

        ###############
        log.info("I'm {} (move_to_production_task)!", self.request.id)
        # local_path = path.join(mybatchpath, batch_id, return_str=True)

        try:
            with celery_app.get_service(service='irods') as imain:

                out_data = []
                errors = []
                counter = 0
                param_key = 'parameters'
                params = myjson.get(param_key, {})
                elements = params.get('pids', {})
                backdoor = params.pop('backdoor', False)
                total = len(elements)
                self.update_state(state="PROGRESS", meta={
                    'total': total, 'step': counter, 'errors': len(errors)})

                if elements is None:
                    return notify_error(
                        ErrorCodes.MISSING_PIDS_LIST,
                        myjson, backdoor, self
                    )

                MAX_RETRIES = 3
                SLEEP_TIME = 10

                for element in elements:

                    temp_id = element.get('temp_id')  # do not pop
                    record_id = element.get('format_n_code')
                    current_file_name = path.last_part(temp_id)
                    # local_element = path.join(local_path, temp_id, return_str=False)
                    batch_file = os.path.join(batch_path, current_file_name)

                    # [fs -> irods]
                    # if path.file_exists_and_nonzero(local_element):
                    #     log.info('Found: {}', local_element)
                    # else:
                    #     log.error('NOT found: {}', local_element)
                    #     errors.append({
                    #         "error": ErrorCodes.INGESTION_FILE_NOT_FOUND[0],
                    #         "description": ErrorCodes.INGESTION_FILE_NOT_FOUND[1],
                    #         "subject": record_id,
                    #     })

                    #     self.update_state(state="PROGRESS", meta={
                    #         'total': total, 'step': counter, 'errors': len(errors)})
                    #     continue

                    if imain.is_dataobject(batch_file):
                        log.info('Found: {}', batch_file)
                    else:
                        log.error('NOT found: {}', batch_file)
                        errors.append({
                            "error": ErrorCodes.INGESTION_FILE_NOT_FOUND[0],
                            "description": ErrorCodes.INGESTION_FILE_NOT_FOUND[1],
                            "subject": record_id,
                        })

                        self.update_state(state="PROGRESS", meta={
                            'total': total, 'step': counter, 'errors': len(errors)})
                        continue

                    ###############
                    # 1. copy file (irods) [fs -> irods]
                    # ifile = path.join(cloud_path, current_file_name, return_str=True)
                    # for i in range(MAX_RETRIES):
                    #     try:
                    #         imain.put(str(local_element), str(ifile))
                    #     except BaseException as e:
                    #         log.error(e)
                    #         time.sleep(SLEEP_TIME)
                    #         continue
                    #     else:
                    #         log.info("File copied on irods: {}", ifile)
                    #         break
                    # else:
                    #     # failed upload for the file
                    #     errors.append({
                    #         "error": ErrorCodes.UNABLE_TO_MOVE_IN_PRODUCTION[0],
                    #         "description": ErrorCodes.UNABLE_TO_MOVE_IN_PRODUCTION[1],
                    #         "subject": record_id,
                    #     })

                    #     self.update_state(state="PROGRESS", meta={
                    #         'total': total, 'step': counter, 'errors': len(errors)})
                    #     continue

                    # 1. copy file (irods) [irods -> irods]
                    ifile = path.join(cloud_path, current_file_name, return_str=True)
                    for i in range(MAX_RETRIES):
                        try:
                            imain.icopy(batch_file, str(ifile))
                        except BaseException as e:
                            log.error(e)
                            time.sleep(SLEEP_TIME)
                            continue
                        else:
                            log.info("File copied on irods: {}", ifile)
                            break
                    else:
                        # failed upload for the file
                        errors.append({
                            "error": ErrorCodes.UNABLE_TO_MOVE_IN_PRODUCTION[0],
                            "description": ErrorCodes.UNABLE_TO_MOVE_IN_PRODUCTION[1],
                            "subject": record_id,
                        })

                        self.update_state(state="PROGRESS", meta={
                            'total': total, 'step': counter, 'errors': len(errors)})
                        continue
                    ###############
                    # 2. request pid (irule)
                    for i in range(MAX_RETRIES):
                        try:
                            if backdoor:
                                log.warning("Backdoor enabled: skipping PID request")
                                PID = "NO_PID_WITH_BACKDOOR"
                            else:
                                PID = pmaker.pid_request(imain, ifile)
                        except BaseException as e:
                            log.error(e)
                            time.sleep(SLEEP_TIME)
                            continue
                        else:
                            log.info('PID: {}', PID)
                            # # save inside the cache
                            r.set(PID, ifile)
                            r.set(ifile, PID)
                            log.debug('PID cache updated')
                            break
                    else:
                        # failed PID assignment
                        errors.append({
                            "error": ErrorCodes.UNABLE_TO_ASSIGN_PID[0],
                            "description": ErrorCodes.UNABLE_TO_ASSIGN_PID[1],
                            "subject": record_id,
                        })

                        self.update_state(state="PROGRESS", meta={
                            'total': total, 'step': counter, 'errors': len(errors)})
                        continue

                    ###############
                    # 3. set metadata (icat)
                    # Remove me in a near future
                    for i in range(MAX_RETRIES):
                        try:
                            metadata, _ = imain.get_metadata(ifile)

                            for key in md.keys:
                                if key not in metadata:
                                    value = element.get(key, '***MISSING***')
                                    args = {'path': ifile, key: value}
                                    imain.set_metadata(**args)
                        except BaseException as e:
                            log.error(e)
                            time.sleep(SLEEP_TIME)
                            continue
                        else:
                            log.debug('Metadata set for {}', current_file_name)
                            break
                    else:
                        # failed metadata setting
                        errors.append({
                            "error": ErrorCodes.UNABLE_TO_SET_METADATA[0],
                            "description": ErrorCodes.UNABLE_TO_SET_METADATA[1],
                            "subject": record_id,
                        })

                        self.update_state(state="PROGRESS", meta={
                            'total': total, 'step': counter, 'errors': len(errors)})
                        continue

                    ###############
                    # 3-bis. set metadata (dataobject)
                    for i in range(MAX_RETRIES):
                        try:
                            content = {}
                            for key in md.keys:
                                value = element.get(key, '***MISSING***')
                                content[key] = value
                            content['PID'] = PID

                            metadata_file = ifile + ".meta"
                            imain.write_file_content(metadata_file, content)
                        except BaseException as e:
                            log.error(e)
                            time.sleep(SLEEP_TIME)
                            continue
                    else:
                        # failed metadata setting
                        errors.append({
                            "error": ErrorCodes.UNABLE_TO_SET_METADATA[0],
                            "description": ErrorCodes.UNABLE_TO_SET_METADATA[1],
                            "subject": record_id,
                        })

                        self.update_state(state="PROGRESS", meta={
                            'total': total, 'step': counter, 'errors': len(errors)})
                        continue
                    ###############
                    # 4. remove the batch file?
                    # or move it into a "completed/" folder
                    # where we can check if it was already done?
                    pass

                    ###############
                    # 5. add to logs
                    element['pid'] = PID
                    out_data.append(element)

                    counter += 1
                    self.update_state(state="PROGRESS", meta={
                        'total': total, 'step': counter, 'errors': len(errors)}
                    )

                ###############
                # Notify the CDI API
                myjson[param_key]['pids'] = out_data
                msg = prepare_message(self, isjson=True)
                for key, value in msg.items():
                    myjson[key] = value
                if len(errors) > 0:
                    myjson['errors'] = errors
                ret = ext_api.post(myjson, backdoor=backdoor)
                log.info('CDI IM CALL = {}', ret)

                out = {
                    'total': total, 'step': counter,
                    'errors': len(errors), 'out': out_data
                }
                self.update_state(state="COMPLETED", meta=out)
                return out
        except BaseException as e:
            log.error(e)
            log.error(type(e))
            return notify_error(
                ErrorCodes.UNEXPECTED_ERROR,
                myjson, backdoor, self
            )

    return myjson
