#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
An example of custom (Restful) flask view.

IMPORTANT:
You need to define a Blueprint called 'restbp' to make this work.
"""

from __future__ import absolute_import
from flask import Blueprint, \
    render_template, make_response, abort
from jinja2 import TemplateNotFound
from flask_restful import Api, Resource

################################
# Using restful blueprint for all classes
bp = Blueprint('someviews', __name__)  # , template_folder='templates')
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

    # def __init__(self):
    #     pass

    def render(self, page='test.html'):
        try:
            return make_response(render_template(page), 200, self._headers)
        except TemplateNotFound:
            abort(404)


# Restful view class
class ToDo(RestView):
    """ A test """
    def get(self):
        return self.render('index.html')

# In the end
rest.add_resource(ToDo, '/todos')
#rest.add_resource(ToDo, '/todos/<int:id>')
################################

# WHAT TO DO LATER WITH BLUEPRINT # app.register_blueprint(bp)
