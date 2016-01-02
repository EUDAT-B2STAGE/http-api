#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Flask application main file """

# Import app factory
from felask.server import create_app
# Configuration is decided via environment variable: FLASK_CONFIGURATION

# #TORNADO
# from tornado.wsgi import WSGIContainer
# from tornado.httpserver import HTTPServer
# from tornado.ioloop import IOLoop
# #GEVENT
# #from gevent.wsgi import WSGIServer


app = create_app()
host = app.config.get("HOST")
port = app.config.get("PORT")
debug = app.config.get("DEBUG")

#debug = False

if __name__ == '__main__':
    # if debug:
        app.run(host=host, port=port, debug=debug, threaded=True)
    # else:
    # #     ## GEVENT
    # #     # http_server = WSGIServer(('', port), app)
    # #     # http_server.serve_forever()
    #     ## TORNADO
    #     http_server = HTTPServer(WSGIContainer(app))
    #     http_server.listen(port)
    #     IOLoop.instance().start()
