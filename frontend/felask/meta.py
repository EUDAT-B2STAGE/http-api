#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Meta thinking: python introspection """

from __future__ import absolute_import
import pkgutil
from importlib import import_module
from config import get_logger

logger = get_logger(__name__)


################################
# Utilities
class Meta(object):
    """Utilities with meta in mind"""

    _latest_list = {}
    _submodules = []

    def get_latest_classes(self):
        return self._latest_list

    def set_latest_classes(self, classes):
        self._latest_list = classes

    def get_submodules_from_package(self, package):
        self._submodules = []
        for importer, modname, ispkg \
                in pkgutil.iter_modules(package.__path__):
            if not ispkg:
                self._submodules.append(modname)
                logger.info("Found %s submodule inside %s" %
                             (modname, package.__name__))
        return self._submodules

    def get_classes_from_module(self, module):
        """ Find classes inside a python module file """
        classes = dict([(name, cls)
                       for name, cls in module.__dict__.items()
                       if isinstance(cls, type)])
        self.set_latest_classes(classes)
        return self.get_latest_classes()

    def get_new_classes_from_module(self, module):
        """ Skip classes not originated inside the module """
        classes = []
        for key, value in self.get_classes_from_module(module).items():
            if module.__name__ in value.__module__:
                classes.append(value)
        self.set_latest_classes(classes)
        return self.get_latest_classes()

    def get_module_from_string(self, modulestring):
        """
        Getting a module import
        when your module is stored as a string in a variable
        """

        module = None
        try:
            # Meta language for dinamically import
            module = import_module(modulestring)
        except ImportError as e:
            logger.warning("Failed to load resource: " + str(e))
        return module

    def get_class_from_string(self, classname, module):
        """ Get a specific class from a module using a string variable """

        myclass = None
        try:
            # Meta language for dinamically import
            myclass = getattr(module, classname)
        except AttributeError as e:
            logger.warning("Failed to load resource: " + str(e))

        return myclass
