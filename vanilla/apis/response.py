# -*- coding: utf-8 -*-

from __future__ import absolute_import

from commons.logs import get_logger
from ..base import ExtendedApiResource
from .. import decorators as decorate

logger = get_logger(__name__)


############################################################
# # OPTION 1

# @decorate.custom_response
# def fedapp_response(
#         defined_content=None,
#         code=None,
#         errors={},
#         headers={}):

#     return ExtendedApiResource.flask_response("Hello")

# # OPTION 2

# class Response(ExtendedApiResource):
#     def fedapp_response(self, *args, **kwargs):
#         return self.flask_response("Hello")

# decorate.custom_response(Response().fedapp_response)

# # OPTION 3
## // TO BE FIXED
# decorate.custom_response(original=True)

############################################################

SERVER_ERROR = {'message': 'Internal Server Error'}


@decorate.custom_response
def eudat_response(*args, defined_content=None, code=None, headers={},
                   errors={}, **kwargs):
    """
    Define my response that will be used
    from any custom endpoint inside any file
    """

    if defined_content is None:
        defined_content = {}
    elif not isinstance(defined_content, dict):
        tmp = defined_content
        defined_content = {'response': tmp}
    elif defined_content == SERVER_ERROR:
        errors = defined_content
        defined_content = None

    if len(args) > 0:
        defined_content['content'] = args

    for key, value in kwargs.items():
        defined_content[key] = value

    if len(errors) > 0:
        defined_content = {'errors': errors}

    return ExtendedApiResource.flask_response(
        defined_content, status=code, headers=headers)
