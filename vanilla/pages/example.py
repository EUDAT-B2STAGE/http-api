#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An example of custom (Restful) flask view.

IMPORTANT:
You need to define a Blueprint called 'restbp' to make this work.
"""

from __future__ import absolute_import
from flask import Blueprint, \
    render_template, make_response
from jinja2 import TemplateNotFound
from flask_restful import Api, Resource

"""
// TO FIX:

* Choose a dynamic template folder
    - based on blueprint name?
    - use variable from config to give the base
* Move base rest view class somewhere
    - also move imports
* Make dynamic assignment of all endpoints on all classes
    - check only the ones which derive from RestView

"""

################################
# Using restful blueprint for all classes
bp = Blueprint('someviews', __name__,
               template_folder='templates')
# Use restful on current blueprint
rest = Api(bp)


# ################################
# # NORMAL WAY
# @bp.route('/', defaults={'page': 'index'})
# @bp.route('/<page>')
# def show(page):
#     try:
#         return render_template('pages/%s.html' % page)
#     except TemplateNotFound:
#         abort(404)


################################
# REST WAY
class RestView(Resource):
    """ A base REST resource for views """
    _headers = {'Content-Type': 'text/html'}
    _endpoint = 'test'

    def __init__(self):
        pass

    def endpoint(self):
        return '/' + self.__class__.__name__.lower()

    def render(self, page='test.html'):
        try:
            return make_response(render_template(page), 200, self._headers)
        except TemplateNotFound:
            return make_response("Failed", 404, self._headers)


# Restful view class
class ToDo(RestView):
    """ A test """
    def get(self):
        return self.render('test.html')

# Add resources
rest.add_resource(ToDo, ToDo().endpoint())
# rest.add_resource(ToDo, '/todos/<int:id>')
################################

# WHAT TO DO LATER WITH BLUEPRINT:
# app.register_blueprint(bp)
