# -*- coding: utf-8 -*-

"""
Rest view implementation
"""

from __future__ import absolute_import
import os
from commons import htmlcodes as hc
from flask import Blueprint, render_template, make_response
from jinja2 import TemplateNotFound
from flask.ext.restful import Api, Resource
from config import get_logger

logger = get_logger(__name__)

CUSTOM_TEMPLATES = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'templates',
    'custom')


#########################
# Use restful plugin
def generate_blueprint(module='module.someviews', classes=[]):
    """ Using restful blueprint for all classes """

    # Recovering the right path for custom templates
    rev = module[::-1]
    name = rev[:rev.index('.')][::-1]
    path = os.path.join(CUSTOM_TEMPLATES, name)
    # Restful blueprint
    bp = Blueprint(name, __name__, template_folder=path)
    rest = Api(bp)
    # Add resources
    for view in classes:
        logger.info("Adding flask view '%s' to blueprint '%s'" % (view, name))
        view._tpath = path
# IS THIS ENOUGH?
        rest.add_resource(view, view().endpoint())
    return bp


class RestView(Resource):
    """ A base REST resource for views """
    _headers = {'Content-Type': 'text/html'}
    _endpoint = 'test'
    _tpath = "/"

    def __init__(self):
        """ Skip normal REST init """
        pass

    def endpoint(self):
        """ Define endpoint name based on class name """
        return '/' + self.__class__.__name__.lower()

    def render(self, page='test.html'):
        """ Render a python template as HTML page """
        try:
            return make_response(render_template(page),
                                 hc.HTTP_OK_BASIC, self._headers)
        except TemplateNotFound:
            message = "Failed to find page '%s' in path '%s'" \
                % (page, self._tpath)
            return make_response(message,
                                 hc.HTTP_BAD_NOTFOUND, self._headers)
