# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from __future__ import absolute_import
from commons.logs import get_logger
from ..base import ExtendedApiResource
from .. import decorators as decorate

# AUTH
# from ...confs import config
# from flask.ext.security import roles_required, auth_token_required

logger = get_logger(__name__)


#####################################
class SomeRestEndpoint(ExtendedApiResource):

    @decorate.apimethod
    def get(self):
        hello = "Hello world"
        logger.info(hello)
        return self.response(hello)
