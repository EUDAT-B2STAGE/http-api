# -*- coding: utf-8 -*-

""" Development configuration """

from . import BaseConfig, get_logger

logger = get_logger(__name__)


class MyConfig(BaseConfig):

    HOST = '0.0.0.0'
    WTF_CSRF_SECRET_KEY = 'a random string'

    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    logger.info("Current config: DEVEL. Keepeing sqllite db.")
