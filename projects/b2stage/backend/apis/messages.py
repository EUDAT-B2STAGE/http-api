# -*- coding: utf-8 -*-

"""
Exchanging messages on a queue
"""

from restapi.rest.definition import EndpointResource
from utilities.logs import get_logger

log = get_logger(__name__)


class Messages(EndpointResource):

    _queue_service = 'rabbit'

    def get(self):

        log.info("Request: read a message")

        self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')
        current_queue = self._args.get('queue')

        # connect
        msg_queue = self.get_service_instance(self._queue_service)
        log.debug("Connected to %s", self._queue_service)

        # send a message
        channel = msg_queue.channel()
        channel.queue_declare(queue=current_queue)

        def callback(ch, method, properties, body):
            print("\n\nReceived: %r" % body)

        # associate callback to queue
        channel.basic_consume(callback, queue=current_queue, no_ack=True)
        # blocking
        channel.start_consuming()

        return "Received?"

    def post(self):

        log.info("Request: post a message")

        self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')
        current_queue = self._args.get('queue')
        msg = self._args.get('message')

        # connect
        msg_queue = self.get_service_instance(self._queue_service)
        log.debug("Connected to %s", self._queue_service)

        # send a message
        channel = msg_queue.channel()
        channel.queue_declare(queue=current_queue)
        channel.basic_publish(exchange='', routing_key=current_queue, body=msg)
        log.info("%s: sent msg '%s'", current_queue, msg)

        # NOTE: bad! all connections would result in closed
        # # close resource
        # msg_queue.close()

        return "[%s] posted '%s'" % (current_queue, msg)
