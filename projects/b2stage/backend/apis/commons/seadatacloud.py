# -*- coding: utf-8 -*-

from restapi.services.detect import detector
SEADATA_ENABLED = detector.get_global_var('SEADATA_PROJECT')


class Empty(object):
    pass
