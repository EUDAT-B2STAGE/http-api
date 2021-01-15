import os
import sys
from socket import gethostname

from b2stage.endpoints.commons.b2handle import PIDgenerator
from restapi.connectors.celery import CeleryExt
from restapi.env import Env
from restapi.utilities.logs import log
from seadata.endpoints.commons.seadatacloud import ImportManagerAPI, seadata_vars

# Size in bytes
# TODO: move me into the configuration
MAX_ZIP_SIZE = 2147483648  # 2 gb
####################

"""
These are the paths of the locations on the
local filesystem inside the celery worker
containers where the data is copied to / expected
to reside.

Note: The bind-mount from the host is defined
in workers.yml, so if you change the /usr/local
here, you need to change it there too.
"""
mount_point = seadata_vars.get("resources_mountpoint")  # '/usr/share'
if mount_point is None:
    log.critical("Unable to obtain variable: SEADATA_RESOURCES_MOUNTPOINT")
    sys.exit(1)
middle_path_ingestion = seadata_vars.get("workspace_ingestion")  # 'ingestion'
middle_path_orders = seadata_vars.get("workspace_orders")  # 'orders'
mybatchpath = os.path.join(mount_point, middle_path_ingestion)
myorderspath = os.path.join(mount_point, middle_path_orders)

ext_api = ImportManagerAPI()

#####################
# https://stackoverflow.com/q/16040039
log.debug("celery: disable prefetching")
# disable prefetching
CeleryExt.celery_app.conf.update(
    # CELERYD_PREFETCH_MULTIPLIER=1,
    # CELERY_ACKS_LATE=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)


# worker connection to redis
def get_redis():
    if gethostname() == "rapydo_server":
        return None
    redis_vars = Env.load_variables_group(prefix="redis")
    from redis import StrictRedis

    # pid_prefix = redis_vars.get('prefix')
    return StrictRedis(redis_vars.get("host"))


r = get_redis()
####################
# preparing b2handle stuff
pmaker = PIDgenerator()


def notify_error(
    error, payload, backdoor, task, extra=None, subject=None, edmo_code=None
):

    error_message = "Error {}: {}".format(error[0], error[1])
    if subject is not None:
        error_message = f"{error_message}. [{subject}]"
    log.error(error_message)
    if extra:
        log.error(str(extra))

    payload["errors"] = []
    e = {
        "error": error[0],
        "description": error[1],
    }
    if subject is not None:
        e["subject"] = subject

    payload["errors"].append(e)

    if backdoor:
        log.warning(
            "You enabled the backdoor: this json will not be sent to ImportManagerAPI"
        )
        log.info(payload)
    else:
        ext_api.post(payload, edmo_code=edmo_code)

    task_errors = [error_message]
    if extra:
        task_errors.append(str(extra))
    task.update_state(state="FAILED", meta={"errors": task_errors})
    return "Failed"
