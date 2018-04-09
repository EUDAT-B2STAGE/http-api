# -*- coding: utf-8 -*-

from restapi.rest.definition import EndpointResource
from utilities.logs import get_logger

log = get_logger(__name__)


class Extlogs(EndpointResource):

    def get(self):

        #################
        log.info("Received HTTP request")
        # self.get_input()
        # log.pp(self._args, prefix_line='Parsed args')

        #################
        # check index?
        # $SERVER/_cat/indices

        #################
        from datetime import datetime
        calendar = datetime.today().strftime("%Y.%m.%d")
        from b2stage.apis.commons.queue import QUEUE_VARS as qvars
        # Add size=100 as param?
        url = '%s://%s:%s/app_%s-%s/_search?q=*:*' % (
            'http', qvars.get('host'), 9200,
            qvars.get('queue'), calendar
        )

        import requests
        r = requests.get(url)
        out = r.json().get('hits', {})
        log.info("Found %s results", out.get('total'))

        # logs = {}
        logs = []
        for result in out.get('hits', []):
            value = result.get('_source', {}).get('parsed_json')
            if value is None:
                continue
            # key = value.pop('datetime')
            # logs[key] = value
            logs.append(value)
        return logs
