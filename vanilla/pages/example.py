#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An example of custom (Restful) flask view.

IMPORTANT:
You need to define a Blueprint called 'restbp' to make this work.
"""

from __future__ import absolute_import
from ..views import RestView, generate_blueprint

"""
// TO FIX:

* Make dynamic assignment of all endpoints on all classes
    - check only the ones which derive from RestView
* Make dynamic load of blueprints inside 'create_app' ...??
* Choose a dynamic template folder
    - based on blueprint name?
    - use variable from config to give the base

"""


# Restful view class
class ToDo(RestView):
    """ A test """
    def get(self):
        return self.render('test.html')

bp = generate_blueprint(__name__,
                        classes=[ToDo],
                        folder='/data/angulask')
