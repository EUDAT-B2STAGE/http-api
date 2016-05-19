# -*- coding: utf-8 -*-

""" Factory a new Flask app """

from __future__ import absolute_import
from flask import Flask, request as req
from config import get_logger
from . import htmlcodes as hcodes
from .pages import cms
from . import CONFIG_MODULE

# TO FIX?
from .basemodel import db, lm

logger = get_logger(__name__)


def create_app():
    """ Create the istance for Flask application """

    ###############################
    # Create a FLASK application
    app = Flask(__name__)
    # Note: since the app is defined inside this file,
    # the static dir will be searched inside this subdirectory

    ###############################
    # Apply configuration
    app.config.from_object(CONFIG_MODULE + '.MyConfig')

    ###############################
    # # Cache
    # # http://flask.pocoo.org/docs/0.10/patterns/caching/#setting-up-a-cache
    # from werkzeug.contrib.cache import SimpleCache
    # cache = SimpleCache()

    ###############################
    # Database
    db.init_app(app)
    # Add basic things to this app
    app.register_blueprint(cms)

    ###############################
    # Flask LOGIN
    lm.init_app(app)
    lm.login_view = '.login'

    ###############################
    # Application context
    with app.app_context():
# GET THE HELL OUT OF HERE
        db.create_all()
        logger.info("Initialized Database")

        # DB SANITY CHECKS?
        # from .sanity_checks import is_sane_database
        # from .models import MyModel
        # # Note, this will check all models, not only MyModel...
        # is_sane_database(MyModel, db.session)

    # Logging
    @app.after_request
    def log_response(resp):
        log = logger.info
        if resp.status_code == hcodes.HTTP_NOT_MODIFIED:
            log = logger.debug
        log("{} {} {} {}".format(req.method, req.url, req.data, resp))
        return resp

    return app
