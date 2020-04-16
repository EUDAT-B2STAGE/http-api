# -*- coding: utf-8 -*-
import os

from restapi.utilities.logs import log


class Initializer(object):

    def __init__(self, services, app=None):

        sql = services.get('sqlalchemy', None)

        if sql is None:
            log.critical("Unable to retrieve sqlalchemy service")
            return

        if app is None:
            log.critical("Unable to retrieve app context")
            return
