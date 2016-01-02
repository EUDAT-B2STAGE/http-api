#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flask app creation
"""

from . import myself, lic, get_logger
import time
from .server import create_app
from confs.config import args

__author__ = myself
__copyright__ = myself
__license__ = lic

logger = get_logger(__name__)

if args.debug:
    logger.warning("Enabling DEBUG mode")
    time.sleep(1)
if not args.security:
    logger.warning("No security enabled! Are you sure??")
    time.sleep(1)

#############################
# BE FLASK
app = create_app(name='API', enable_security=args.security, debug=args.debug)
# We are now ready
logger.info("*** Our REST API server/app is ready ***")
# Some code may take this app from here
