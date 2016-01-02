#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
First base: RESTful API python3 flask server
"""

from restapi.app import app
from confs.config import SERVER_HOSTS, SERVER_PORT

if __name__ == "__main__":
    app.run(host=SERVER_HOSTS, port=SERVER_PORT)
