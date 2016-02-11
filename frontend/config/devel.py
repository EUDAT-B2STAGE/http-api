# -*- coding: utf-8 -*-

""" Development configuration """

import os
from config import BaseConfig, get_logger

logger = get_logger(__name__)


class MyConfig(BaseConfig):

    HOST = '0.0.0.0'
    WTF_CSRF_SECRET_KEY = 'a random string'

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_FOLDER = '/uploads'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    logger.info("Current config: DEVEL. Keepeing sqllite db.")
