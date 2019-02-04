# -*- coding: utf-8 -*-

from restapi.rest.definition import EndpointResource
from utilities.logs import get_logger

log = get_logger(__name__)


class Extlogs(EndpointResource):

    def get(self):

        from restapi.confs import PRODUCTION
        if not PRODUCTION:
            return 'Not working in DEBUG mode'
        else:
            log.info("Request logs content")

        # check index?
        # $SERVER/_cat/indices

        ################################
        # FIXME: move into elastic
        from datetime import datetime
        calendar = datetime.today().strftime("%Y.%m.%d")

        ################################
        # FIXME: remove this vars
        from b2stage.apis.commons.queue import QUEUE_VARS as qvars
        # Add size=100 as param?
        url = '%s://%s:%s/app_%s-%s/_search?q=*:*' % (
            'http', qvars.get('host'), 9200,
            qvars.get('queue'), calendar
        )
        log.debug("Index URL: %s", url)

        ################################
        # FIXME: use flask_elastic instance
        import requests
        r = requests.get(url)
        out = r.json().get('hits', {})
        log.info("Found %s results", out.get('total'))

        ################################
        # logs = {}
        logs = []
        for result in out.get('hits', []):
            source = result.get('_source', {})
            value = source.get('parsed_json')
            if value is None:
                # tmp = source.get('message')
                # import json
                # value = json.loads(tmp)
                continue

            # key = value.pop('datetime')
            # logs[key] = value
            logs.append(value)
        return logs
