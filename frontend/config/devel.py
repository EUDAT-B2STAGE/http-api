# -*- coding: utf-8 -*-

""" Development configuration """

from . import BaseConfig
from commons.logs import get_logger

logger = get_logger(__name__)


class MyConfig(BaseConfig):

    HOST = '0.0.0.0'
    WTF_CSRF_SECRET_KEY = 'a random string'
    LOG_DEBUG = False
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    logger.info("Current config: DEVEL. Keepeing sqllite db.")
