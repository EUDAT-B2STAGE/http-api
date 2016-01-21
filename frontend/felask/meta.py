# -*- coding: utf-8 -*-

"""
Meta thinking: python objects & introspection

usefull documentation:
http://python-3-patterns-idioms-test.readthedocs.org/en/latest/Metaprogramming.html
"""

from importlib import import_module
import pkgutil
from . import get_logger

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
                logger.debug("Found %s submodule inside %s" %
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
        """ Getting a module import
        when your module is stored as a string in a variable """

        module = None
        try:
            # Meta language for dinamically import
            module = import_module(modulestring)
        except ImportError as e:
            logger.critical("Failed to load resource: " + str(e))
        return module

    def get_class_from_string(self, classname, module):
        """ Get a specific class from a module using a string variable """

        myclass = None
        try:
            # Meta language for dinamically import
            myclass = getattr(module, classname)
        except AttributeError as e:
            logger.critical("Failed to load resource: " + str(e))

        return myclass

    @staticmethod
    def metaclassing(your_class, label=None, attributes={}):
        """
        Creating a class using metas.
        Very usefull for automatic algorithms.
        """
        methods = dict(your_class.__dict__)
        for key, value in attributes.items():
            methods.update({key: value})
        return type(label, (your_class,), methods)


######################################################
# ## INTERESTING EXAMPLE OF CREATING META CLASSES ## #

# with open(fileschema) as f:
#     mytemplate = json.load(f)
# reference_schema = convert_to_marshal(mytemplate)

# # Name for the class. Remove path and extension (json)
# label = os.path.splitext(
#     os.path.basename(fileschema))[0].lower()
# # Dynamic attributes
# new_attributes = {
#     "schema": reference_schema,
#     "template": mytemplate,
#     "table": label,
# }
# # Generating the new class
# from ...meta import Meta
# resource_class = RethinkResource
# if secured:
#     resource_class = RethinkSecuredResource
# newclass = Meta.metaclassing(resource_class, label, new_attributes)
# # Using the same structure i previously used in resources:
# # resources[name] = (new_class, data_model.table)
# json_autoresources[label] = (newclass, label)

######################################################
