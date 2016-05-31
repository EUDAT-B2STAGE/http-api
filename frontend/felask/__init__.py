# -*- coding: utf-8 -*-

""" Factory and blueprints patterns """

import os
from config import get_logger
from commons.meta import Meta as m

logger = get_logger(__name__)

################
config = {
    "default": "config.devel",
    "development": "config.devel",
    "production": "config.prod",
    # "testing": "bookshelf.config.TestingConfig",
}
config_name = os.getenv('FLASK_CONFIGURATION', 'default')
CONFIG_MODULE = config[config_name]
configuration_module = m().get_module_from_string(CONFIG_MODULE)

logger.debug("Configuration:\t%s in [%s]" % (config_name, CONFIG_MODULE))
