# -*- coding: utf-8 -*-

"""
close the rabbit connection when the HTTP API finish
    - catch the sigkill?
    - deconstructor in the flask ext?
    - check connection errors
"""

import json
import pika
import copy
from restapi.services.detect import detector
from utilities.logs import get_logger

log = get_logger(__name__)

QUEUE_SERVICE = 'rabbit'
QUEUE_VARS = detector.load_group(label=QUEUE_SERVICE)

'''
:param instance: The Endpoint.
:param params: The kv pairs to be in the log message.

'''
def prepare_message(instance, **params):
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
    logmsg['request_id'] = instance_id
    # logmsg['request_id'] = instance_id[len(instance_id) - 6:]

    # WRONG EDMO CODE!
    #from b2stage.apis.commons.seadatacloud import seadata_vars
    #logmsg['edmo_code'] = seadata_vars.get('edmo_code')

    from datetime import datetime
    logmsg['datetime'] = datetime.now().strftime("%Y%m%dT%H:%M:%S")

    from restapi.services.authentication import BaseAuthentication as Service
    ip, _ = Service.get_host_info()
    logmsg['ip_number'] = ip
    # logmsg['hostname'] = hostname

    from flask import request
    import re
    endpoint = re.sub(r"https?://[^\/]+", '', request.url)
    logmsg['program'] = request.method + ':' + endpoint

    # WRONG USER?
    #if user is None:
    #    user = 'import_manager' # TODO: True? Not sure!
    #logmsg['user'] = user

    # log.pp(logmsg)
    return logmsg

def _log_any(instance, taskname, dictio, maris_params):
    # Only to be used by functions in this module

    # Make sure we don't log 100s of files,
    # by replacing ref to pid-list by ref to
    # shorter pid list, but in a copy, not in
    # original param!
    # TODO We probably need something similar for orders!
    if 'parameters' in maris_params and 'pids' in maris_params['parameters']:
        if len(maris_params['parameters']['pids']) > 3:
            temp1 = copy.copy(maris_params)               # must be shallow
            temp2 = copy.copy(maris_params['parameters']) # must be shallow!
            few_pids = [
                maris_params['parameters']['pids'][0],
                maris_params['parameters']['pids'][1],
                '...'
            ]
            temp2['pids'] = few_pids
            temp1['parameters'] = temp2
            maris_params = temp1 # only change pointer
            
    combi = {**dictio, **maris_params}
    combi['taskname']=taskname
    msg = prepare_message(instance, **combi)
    _log_into_queue(instance, combi)


def log_start(instance, taskname, maris_params, descrip=''):
    # Log the start of any operation
    dictio = {'progress': 'start'}
    _log_any(instance, taskname, dictio, maris_params)

def log_failure(instance, taskname, maris_params, descrip):
    # Log any errors that return http error codes
    # TODO Better for elastic to have alwayds the same fields?
    dictio = {
        'progress': 'failure',
        'info': {
            'descrip': descrip
        }
    }
    _log_any(instance, taskname, dictio, maris_params)

def log_success(instance, taskname, maris_params, status, descrip=None):
    # Logging the end of a synchronous task
    # or the end of an asynchronous task.
    # NOT: When asynchronous was submitted!
    dictio = {
        'progress': 'end_success',
        'info': {
            'status': status,
            'descrip': descrip
        }
    }
    _log_any(instance, taskname, dictio, maris_params)


def log_submitted(instance, taskname, maris_params, async_id):
    # An async task was submitted to celery
    dictio = {
        'progress': 'submitted',
        'info': {'async_id': async_id}
    }
    _log_any(instance, taskname, dictio, maris_params)


def log_progress(instance, taskname, maris_params, descrip):
    # Can be used to log any logworthy progress
    dictio = {
        'progress': 'intermediate',
        'info' : descrip
    }
    _log_any(instance, taskname, dictio, maris_params)


def log_async_start(instance, taskname, maris_params):
    # An async task has been picked up by a worker
    dictio = {'progress': 'picked_up'}
    _log_any(instance, taskname, dictio, maris_params)


def log_success_uncertain(instance, taskname, maris_params, descrip):
    # When we are not sure whether the task was successful
    dictio = {
        'progress': 'end_uncertain',
        'info': descrip
    }
    _log_any(instance, taskname, dictio, maris_params)


'''
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
'''
def _log_into_queue(instance, dictionary_message):
    """ RabbitMQ in the EUDAT infrastructure """

    log.verbose('LOG MESSAGE to be passed to log-queue: %s ' % dictionary_message)

    current_exchange = QUEUE_VARS.get('exchange')
    routing_key = QUEUE_VARS.get('routing_key')
    app_name = QUEUE_VARS.get('app_name')

    if app_name is None:
        app_name = routing_key

    log.debug('Log-queue service: exchange "%s", routing key "%s", app name "%s"' % (current_exchange, routing_key, app_name))

    try:

        # Error seem to be raised if we don't refresh connection?
        # https://github.com/pika/pika/issues/397#issuecomment-35322410
        # --> Has to be handled in rapydo/http-api, where connection is defined!

        msg_queue = instance.get_service_instance(QUEUE_SERVICE)
        log.verbose('Retrieved instance of log-queue service "%s"', QUEUE_SERVICE)
        msg_queue.log_json_to_queue(dictionary_message, app_name, current_exchange, routing_key)


    except BaseException as e:
        log.error("Failed to log:\n%s(%s)", e.__class__.__name__, e)
    else:
        log.verbose('Log message passed to log-queue service.')
        # log.verbose("%s: sent msg '%s'", routing_key, dictionary_message)

        # NOTE: bad! all connections would result in closed
        # # close resource
        # msg_queue.close()
        # FIXME: Close it elsewhere! Catching sigkill for example.

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
