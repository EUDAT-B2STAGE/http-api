"""
close the rabbit connection when the HTTP API finish
    - catch the sigkill?
    - deconstructor in the flask ext?
    - check connection errors
"""

import re
from datetime import datetime

from flask import request
from restapi.connectors import rabbitmq
from restapi.env import Env
from restapi.services.authentication import BaseAuthentication
from restapi.utilities.logs import log
from seadata.endpoints.commons.seadatacloud import seadata_vars

QUEUE_VARS = Env.load_group(label="rabbit")

"""
:param instance: The Endpoint.
:param params: The kv pairs to be in the log message.

"""


def prepare_message(instance, user=None, get_json=False, **params):
    """
{ # start
    "request_id": # build a hash for the current request
    "edmo_code": # which eudat centre is
    "json": "the json input file" # parameters maris
    "datetime":"20180328T10:08:30", # timestamp
    "ip_number":"544.544.544.544", # request.remote_addr
    "program":"program/function name", # what's mine?
    "url" ?
    "user":"username", # from maris? marine id?
    "log_string":"start"
}

{ # end
    "datetime":"20180328T10:08:30",
    "request_id":"from the json input file",
    "ip_number":"544.544.544.544",
    "program":"program of function = name",
    "user":"username",
    "edmo_code":"sample 353",
    "log_string":"end"
}
    """
    logmsg = dict(params)

    instance_id = str(id(instance))
    logmsg["request_id"] = instance_id

    logmsg["edmo_code"] = seadata_vars.get("edmo_code")

    logmsg["datetime"] = datetime.now().strftime("%Y%m%dT%H:%M:%S")

    if get_json:
        return logmsg

    ip = BaseAuthentication.get_remote_ip()
    logmsg["ip_number"] = ip

    # http://localhost:8080/api/pids/<PID>

    endpoint = re.sub(r"https?://[^\/]+", "", request.url)
    logmsg["program"] = request.method + ":" + endpoint
    if user is None:
        user = "import_manager"  # TODO: True? Not sure!
    logmsg["user"] = user

    return logmsg


"""
Send a log message into the logging queue, so that it
ends up in ElasticSearch.

It needs the following info from config:

* RABBIT_EXCHANGE (where the message is sent to to be
    distributed to a queue).
* RABBIT_QUEUE (will be used as routing key to route the
    message to the correct queue).
* RABBIT_APP_NAME (will determine the name of the
    ElasticSearch index where the message will be stored.
    If not provided, the value of RABBIT_QUEUE will be used).

:param instance: Instance of the Logging service from rapydo.
:param dictionary_message: The message to be logged (as JSON).
"""


def log_into_queue(instance, dictionary_message):
    """ RabbitMQ in the EUDAT infrastructure """

    # temporary disabled
    return False

    log.debug("LOG MESSAGE to be passed to log-queue: {}", dictionary_message)

    exchange = QUEUE_VARS.get("exchange")
    routing_key = QUEUE_VARS.get("queue")
    app_name = QUEUE_VARS.get("app_name")

    if app_name is None:
        app_name = routing_key

    log.debug(
        'Log-queue service: exchange "{}", routing key "{}", app name "{}"',
        exchange,
        routing_key,
        app_name,
    )

    try:

        rabbit = rabbitmq.get_instance()
        log.debug("Retrieved instance of RabbitMQ service")
        rabbit.send_json(
            dictionary_message,
            routing_key=routing_key,
            exchange=exchange,
            headers={
                "app_name": app_name,
                "filter_code": "de.dkrz.seadata.filter_code.json",
            },
        )

    except BaseException as e:
        log.error("Failed to send log: {} ({})", e.__class__.__name__, e)
    else:
        log.debug("Log message sent to queue service.")

    return True
