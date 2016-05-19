# -*- coding: utf-8 -*-

""" Development configuration """

import os

from . import BaseConfig, get_logger

logger = get_logger(__name__)


class MyConfig(BaseConfig):
    HOST = '0.0.0.0'
    LOG_DEBUG = False
    WTF_CSRF_SECRET_KEY = 'a production random string'

    try:
        # We have POSTGRESQL. Use docker environment variables
        dbhost = os.environ["DB_NAME"].split('/')[2]
        dbport = int(os.environ["DB_PORT"].split(':')[2])
        dbuser = os.environ["DB_ENV_POSTGRES_USER"]
        dbpw = os.environ["DB_ENV_POSTGRES_PASSWORD"]
        database = os.environ["DB_ENV_POSTGRES_DB"]
        dbdriver = "postgresql"

        SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%d/%s" \
            % (dbdriver, dbuser, dbpw, dbhost, dbport, database)
    except Exception:
        logger.warning(
            "Cannot found a postgres database instance. Switching to sqllite.")
