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


class QueueMessages(object):

    """ RabbitMQ in the EUDAT infrastructure """

    def log_into_queue(self, dictionary_message):
        """
        # user: username (Marine ID)
        # TODO: get the marine id from ifremer
        # ipnumber
        # timestamp of the request (my time)
        # url (server + endpoint)
        # parameters maris
        """

        ############
        # LOGGING

        current_exchange = QUEUE_VARS.get('exchange')
        current_queue = QUEUE_VARS.get('queue')
        # FIXME: as variables
        filter_code = 'de.dkrz.seadata.filter_code.foo.json'
        app_name = 'requestlogs'

        # connect
        msg_queue = self.get_service_instance(QUEUE_SERVICE)
        log.debug("Connected to %s", QUEUE_SERVICE)

        ############
        # send a message

        # not necessary if already exists (it should)
        # channel.queue_declare(queue=current_queue)
        channel = msg_queue.channel()

        # dictionary_message = {
        #     'test': 1, 'some': 'state',
        #     'request_user': 'paolo',
        #     'valid': ["one", "two"]
        # }

        channel.basic_publish(
            exchange=current_exchange, routing_key=current_queue,
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers={'app_name': app_name, 'filter_code': filter_code},
            ),
            body=json.dumps(dictionary_message),
        )

        ############
        log.info("%s: sent msg '%s'", current_queue, dictionary_message)
        # NOTE: bad! all connections would result in closed
        # # close resource
        # msg_queue.close()
        return True
