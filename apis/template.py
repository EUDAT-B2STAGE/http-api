# -*- coding: utf-8 -*-

""" TEMPLATE """

from __future__ import absolute_import
from ..rest.definition import EndpointResource


class NewEndpoint(EndpointResource):

    def get(self):
        return "Hello world!"
