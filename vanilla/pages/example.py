#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An example of custom (Restful) flask view.

VERY IMPORTANT:
You need to define a Blueprint variable called 'bp' to make this work.
"""

from __future__ import absolute_import
from ..views import RestView, generate_blueprint


# Restful view class
class ToDo(RestView):
    """ A test """
    def get(self):
        return self.render('test.html')

bp = generate_blueprint(__name__, classes=[ToDo])
