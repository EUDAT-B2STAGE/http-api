# -*- coding: utf-8 -*-

"""
close the rabbit connection when the HTTP API finish
    - catch the sigkill?
    - deconstructor in the flask ext?
    - check connection errors
"""

import json
import pika
from restapi.services.detect import detector
from utilities.logs import get_logger

log = get_logger(__name__)

QUEUE_SERVICE = 'rabbit'
QUEUE_VARS = detector.load_group(label=QUEUE_SERVICE)


def prepare_message(instance, user=None, **params):
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
    obj = dict(params)

    instance_id = str(id(instance))
    obj['request_id'] = instance_id
    # obj['request_id'] = instance_id[len(instance_id) - 6:]

    from b2stage.apis.commons.seadatacloud import seadata_vars
    obj['edmo_code'] = seadata_vars.get('edmo_code')

    from datetime import datetime
    obj['datetime'] = datetime.now().strftime("%Y%m%dT%H:%M:%S")

    from restapi.services.authentication import BaseAuthentication as Service
    ip, _ = Service.get_host_info()
    obj['ip_number'] = ip
    # obj['hostname'] = hostname

    from flask import request
    # http://localhost:8080/api/pids/<PID>
    import re
    endpoint = re.sub(r"https?://[^\/]+", '', request.url)
    obj['program'] = request.method + ':' + endpoint
    if user is None:
        user = 'import_manager'
    obj['user'] = user

    # log.pp(obj)
    return obj


def log_into_queue(instance, dictionary_message):
    """ RabbitMQ in the EUDAT infrastructure """

    ############
    from restapi.confs import PRODUCTION
    if not PRODUCTION:
        return False

    ############
    # LOGGING

    current_exchange = QUEUE_VARS.get('exchange')
    current_queue = QUEUE_VARS.get('queue')
    # FIXME: as variables
    filter_code = 'de.dkrz.seadata.filter_code.foo.json'
    # app_name = 'requestlogs'
    # app_name = 'maris_elk_test'
    app_name = current_queue

    try:
        # connect
        msg_queue = instance.get_service_instance(QUEUE_SERVICE)
        log.verbose("Connected to %s", QUEUE_SERVICE)
        # channel.queue_declare(queue=current_queue)  # not necessary if exists
        channel = msg_queue.channel()  # send a message
        channel.basic_publish(
            exchange=current_exchange, routing_key=current_queue,
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers={'app_name': app_name, 'filter_code': filter_code},
            ),
            body=json.dumps(dictionary_message),
        )
    except BaseException as e:
        log.error("Failed to log:\n%s(%s)", e.__class__.__name__, e)
    else:
        log.verbose('Queue msg sent')
        # log.verbose("%s: sent msg '%s'", current_queue, dictionary_message)

        # NOTE: bad! all connections would result in closed
        # # close resource
        # msg_queue.close()

    return True


# def read(self):

#     # log.info("Request: read a message")

#     # self.get_input()
#     # # log.pp(self._args, prefix_line='Parsed args')
#     # current_queue = self._args.get('queue')

#     # # connect
#     # msg_queue = self.get_service_instance(self._queue_service)
#     # log.debug("Connected to %s", self._queue_service)

#     # # send a message
#     # channel = msg_queue.channel()
#     # channel.queue_declare(queue=current_queue)

#     # def callback(ch, method, properties, body):
#     #     print("\n\nReceived: %r" % body)
#     #     import json
#     #     print(json.loads(body))

#     # # associate callback to queue
#     # channel.basic_consume(callback, queue=current_queue, no_ack=True)
#     # # blocking
#     # channel.start_consuming()

#     # return "Received?"

#     raise NotADirectoryError("Not available at the moment")
