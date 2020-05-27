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
def delete_orders(self, orders_path, local_orders_path, myjson):

    with celery_app.app.app_context():

        if 'parameters' not in myjson:
            myjson['parameters'] = {}
            # TODO Raise error already here!
            # Or even before reaching asynchronous job..

        backdoor = glom(myjson, "parameters.backdoor", default=False)

        if 'request_id'not in myjson:
            return notify_error(
                ErrorCodes. MISSING_REQUEST_ID,
                myjson, backdoor, self
            )

        myjson['parameters']['request_id'] = myjson['request_id']
        myjson['request_id'] = self.request.id
        # TODO Why? We end up with two different request_ids,
        # one from the client, one from our system.

        # params = myjson.get('parameters', {})

        orders = myjson['parameters'].pop('orders', None)
        if orders is None:
            return notify_error(
                ErrorCodes.MISSING_ORDERS_PARAMETER,
                myjson, backdoor, self
            )
        total = len(orders)

        if total == 0:
            return notify_error(
                ErrorCodes.EMPTY_ORDERS_PARAMETER,
                myjson, backdoor, self
            )

        try:
            with celery_app.get_service(service='irods') as imain:

                errors = []
                counter = 0
                for order in orders:

                    counter += 1
                    self.update_state(state="PROGRESS", meta={
                        'total': total, 'step': counter, 'errors': len(errors)})

                    order_path = path.join(orders_path, order)
                    local_order_path = path.join(local_orders_path, order)
                    log.info("Delete request for order collection: {}", order_path)
                    log.info("Delete request for order path: {}", local_order_path)

                    if not imain.is_collection(order_path):
                        errors.append({
                            "error": ErrorCodes.ORDER_NOT_FOUND[0],
                            "description": ErrorCodes.ORDER_NOT_FOUND[1],
                            "subject": order,
                        })

                        self.update_state(state="PROGRESS", meta={
                            'total': total, 'step': counter, 'errors': len(errors)})
                        continue

                    ##################
                    # TODO: remove the iticket?

                    # TODO: I should also revoke the task?

                    imain.remove(order_path, recursive=True)

                    if os.path.isdir(str(local_order_path)):
                        rmtree(str(local_order_path), ignore_errors=True)

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
