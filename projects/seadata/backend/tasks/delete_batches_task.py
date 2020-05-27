# -*- coding: utf-8 -*-
import os
from shutil import rmtree
from glom import glom

from seadata.tasks.seadata import ext_api, celery_app
from seadata.tasks.seadata import notify_error
from seadata.apis.commons.seadatacloud import ErrorCodes

from b2stage.apis.commons import path

from restapi.connectors.celery import send_errors_by_email
from restapi.utilities.logs import log


@celery_app.task(bind=True)
@send_errors_by_email
def delete_batches(self, batches_path, local_batches_path, myjson):

    with celery_app.app.app_context():

        if 'parameters' not in myjson:
            myjson['parameters'] = {}

        backdoor = glom(myjson, "parameters.backdoor", default=False)

        if 'request_id'not in myjson:
            return notify_error(
                ErrorCodes. MISSING_REQUEST_ID,
                myjson, backdoor, self
            )

        myjson['parameters']['request_id'] = myjson['request_id']
        myjson['request_id'] = self.request.id

        # params = myjson.get('parameters', {})

        batches = myjson['parameters'].pop('batches', None)
        if batches is None:
            return notify_error(
                ErrorCodes.MISSING_BATCHES_PARAMETER,
                myjson, backdoor, self
            )
        total = len(batches)

        if total == 0:
            return notify_error(
                ErrorCodes.EMPTY_BATCHES_PARAMETER,
                myjson, backdoor, self
            )

        try:
            with celery_app.get_service(service='irods') as imain:

                errors = []
                counter = 0
                for batch in batches:

                    counter += 1
                    self.update_state(state="PROGRESS", meta={
                        'total': total, 'step': counter, 'errors': len(errors)})

                    batch_path = path.join(batches_path, batch)
                    local_batch_path = path.join(local_batches_path, batch)
                    log.info("Delete request for batch collection {}", batch_path)
                    log.info("Delete request for batch path {}", local_batch_path)

                    if not imain.is_collection(batch_path):
                        errors.append({
                            "error": ErrorCodes.BATCH_NOT_FOUND[0],
                            "description": ErrorCodes.BATCH_NOT_FOUND[1],
                            "subject": batch,
                        })

                        self.update_state(state="PROGRESS", meta={
                            'total': total, 'step': counter, 'errors': len(errors)})
                        continue
                    imain.remove(batch_path, recursive=True)

                    if os.path.isdir(str(local_batch_path)):
                        rmtree(str(local_batch_path), ignore_errors=True)

                if len(errors) > 0:
                    myjson['errors'] = errors
                ret = ext_api.post(myjson, backdoor=backdoor)
                log.info('CDI IM CALL = {}', ret)
                return "COMPLETED"
        except BaseException as e:
            log.error(e)
            log.error(type(e))
            return notify_error(
                ErrorCodes.UNEXPECTED_ERROR,
                myjson, backdoor, self
            )
