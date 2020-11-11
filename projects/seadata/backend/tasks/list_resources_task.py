from b2stage.connectors import irods
from restapi.connectors.celery import send_errors_by_email
from restapi.utilities.logs import log
from restapi.utilities.processes import start_timeout, stop_timeout
from seadata.endpoints.commons.seadatacloud import ErrorCodes
from seadata.tasks.seadata import celery_app, ext_api, notify_error

TIMEOUT = 180


@celery_app.task(bind=True)
@send_errors_by_email
def list_resources(self, batch_path, order_path, myjson):

    with celery_app.app.app_context():

        try:
            with irods.get_instance() as imain:

                param_key = "parameters"

                if param_key not in myjson:
                    myjson[param_key] = {}

                myjson[param_key]["request_id"] = myjson["request_id"]
                myjson["request_id"] = self.request.id

                params = myjson.get(param_key, {})
                backdoor = params.pop("backdoor", False)

                if param_key not in myjson:
                    myjson[param_key] = {}

                myjson[param_key]["batches"] = []
                try:
                    start_timeout(TIMEOUT)
                    batches = imain.list(batch_path)
                    for n in batches:
                        myjson[param_key]["batches"].append(n)

                    myjson[param_key]["orders"] = []
                    orders = imain.list(order_path)
                    for n in orders:
                        myjson[param_key]["orders"].append(n)

                    ret = ext_api.post(myjson, backdoor=backdoor)
                    log.info("CDI IM CALL = {}", ret)
                    stop_timeout()
                except BaseException as e:
                    log.error(e)
                    return notify_error(
                        ErrorCodes.UNEXPECTED_ERROR, myjson, backdoor, self
                    )

                return "COMPLETED"
        except BaseException as e:
            log.error(e)
            log.error(type(e))
            return notify_error(ErrorCodes.UNEXPECTED_ERROR, myjson, backdoor, self)
