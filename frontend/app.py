#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Flask application main file """

import os
# Import app factory
from felask.server import create_app
# Configuration is decided via environment variable: FLASK_CONFIGURATION

from plumbum.cmd import ln
from plumbum.commands.processes import ProcessExecutionError as perror

# Productions services
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from gevent.wsgi import WSGIServer
# from config import UPLOAD_FOLDER

#########################
# Decide which WSGI
GEVENT = True
TORNADO = False

#########################
# APP preparation

app = create_app()
host = app.config.get("HOST")
port = app.config.get("PORT")
debug = app.config.get("DEBUG")

# #########################
# # DIRECTORIES preparation

# current_package = create_app.__module__.split('.')[0]
# upload_link = os.path.join(
#     app.config['BASE_DIR'],
#     '../' + current_package + '/static' + UPLOAD_FOLDER)

# try:
#     ln['-s', UPLOAD_FOLDER, upload_link]()
#     app.logger.info("Created folder upload link")
# except perror:
#     pass

#########################
# MAIN
if __name__ == '__main__':
    if debug:
        app.logger.debug("Server is development Flask instance")
        app.run(
            host=host, port=port,
            debug=debug, use_reloader=True, threaded=True)
    else:

        if TORNADO:
            app.logger.info("Tornado mode on")
        # more info:
        # http://www.tornadoweb.org/en/stable/guide/running.html#processes-and-ports

            http_server = HTTPServer(WSGIContainer(app))
            # http_server.listen(port)
            http_server.bind(port)
            http_server.start(0)  # forks one process per cpu
            # IOLoop.istance().start()
            IOLoop.current().start()

        elif GEVENT:
            app.logger.info("GEVENT mode on!")
            http_server = WSGIServer(('', port), app)
            http_server.serve_forever()
