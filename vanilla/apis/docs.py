# -*- coding: utf-8 -*-

"""
Some endpoints implementation
"""

from __future__ import absolute_import
import os
import commentjson as json
import rethinkdb as r
from ..services.rethink import RDBquery, JSONS_PATH, JSONS_EXT
from ..base import ExtendedApiResource
from .. import decorators as deck
from flask.ext.security import auth_token_required  # , roles_required
from flask import request, url_for, redirect
from ...marshal import convert_to_marshal
from ... import htmlcodes as hcodes
from ... import get_logger

logger = get_logger(__name__)


def schema_and_tables(fileschema):
    """
    This function can recover basic data for my JSON resources
    """
    template = None
    with open(os.path.join(JSONS_PATH, fileschema + JSONS_EXT)) as f:
        template = json.load(f)
    reference_schema = convert_to_marshal(template)
    label = os.path.splitext(
        os.path.basename(fileschema))[0].lower()

    return label, template, reference_schema


#####################################
# Base implementation for methods?
class BaseRethinkResource(ExtendedApiResource, RDBquery):
    """ The json endpoint in a rethinkdb base class """

    def get(self, data_key=None):
        """
        Obtain main data.
        Obtain single objects.
        Filter with predefined queries.
        """

        # Check arguments
        limit = self._args['perpage']
# // TO FIX: use it!
        current_page = self._args['currentpage']

        return self.get_content(data_key, limit)

    def post(self):
        valid = False

        # Get JSON. The power of having a real object in our hand.
        json_data = request.get_json(force=True)

        for key, obj in json_data.items():
            if key in self.schema:
                valid = True
        if not valid:
            return self.template, hcodes.HTTP_BAD_REQUEST

        # marshal_data = marshal(json_data, self.schema, envelope='data')
        myid = self.insert(json_data)

        # redirect to GET method of this same endpoint, with the id found
        address = url_for(self.table, data_key=myid)
        return redirect(address)

#####################################
# Main resource
model = 'datavalues'
mylabel, mytemplate, myschema = schema_and_tables(model)


@deck.enable_endpoint_identifier('data_key')
class RethinkDataValues(BaseRethinkResource):
    """ Data values """

    schema = myschema
    template = mytemplate
    table = mylabel
    table_index = 'record'

    def get_autocomplete_data(self, q, step_number=1, field_number=1):
        """ Data for autocompletion in js """
        return q \
            .concat_map(r.row['steps']) \
            .filter(
                lambda row: row['step'] == step_number
            ).concat_map(r.row['data']) \
            .filter(
                lambda row: row['position'] == field_number
            ).pluck('value').distinct()['value']

    def single_element(self, data):
        """ If I request here one single document """
        single = []
        for steps in data.pop()['steps']:
            element = ""
            for row in steps['data']:
                if row['position'] != 1:
                    continue
                element = row['value']
            single.insert(steps['step'], element)
        return single

    @deck.add_endpoint_parameter(name='filter', ptype=str)
    @deck.add_endpoint_parameter(name='step', ptype=int, default=1)
    @deck.apimethod
    #@auth_token_required
    def get(self, data_key=None):
        data = []
        count = len(data)
        param = self._args['filter']

        if param is not None:
            # Making filtering queries
            logger.debug("Build query '%s'" % param)
            query = self.get_table_query()

            if param == 'autocompletion':
                query = self.get_autocomplete_data(
                    query, self._args['step'])

            # Execute query
            count, data = self.execute_query(query, self._args['perpage'])
        else:
            # Get all content from db
            count, data = super().get(data_key)
            # just one single ID - reshape!
            if data_key is not None:
                data = self.single_element(data)

        return self.response(data, elements=count)

#####################################
# Keys for templates and submission
model = 'datakeys'
mylabel, mytemplate, myschema = schema_and_tables(model)


# # // TO FIX
# // Does this work if it's only one?
#@deck.enable_endpoint_identifier('step')
class RethinkDataKeys(BaseRethinkResource):
    """ Data keys administrable """

    schema = myschema
    template = mytemplate
    table = mylabel
    table_index = 'steps'

# # // TO FIX
#     def __init__(self):
#         self.set_method_id('step', 'int')
#         super(RethinkDataKeys, self).__init__()
# # // TO FIX

    @deck.apimethod
    @auth_token_required
    def get(self, step=None):
        count, data = super().get(step)
        return self.response(data, elements=count)

#####################################
# Keys for templates and submission
model = 'datadocs'
mylabel, mytemplate, myschema = schema_and_tables(model)


class RethinkDocuments(BaseRethinkResource):
    """ Data keys administrable """

    schema = myschema
    template = mytemplate
    table = mylabel
    table_index = 'record'

    def __init__(self):
        self.set_method_id('data_key')
        super(RethinkDocuments, self).__init__()

    def get_all_notes(self, q):
        return q.concat_map(
            lambda doc: doc['images'].
            has_fields({'transcriptions': True}).concat_map(
                lambda image: image['transcriptions_split'])) \
            .distinct()

    def get_filtered_notes(self, q, filter_value=None):
        """ Data for autocompletion in js """

        mapped = q.concat_map(
                lambda doc: doc['images'].has_fields(
                    {'transcriptions': True}).map(
                        lambda image: {
                            'word': image['transcriptions_split'],
                            'record': doc['record'],
                        }
                    )).distinct()

        if filter_value is not None:
            return mapped.filter(
                lambda mapped: mapped['word'].contains(filter_value))

        return mapped

    @deck.add_endpoint_parameter(name='filter')
    @deck.add_endpoint_parameter(name='key')
    @deck.apimethod
    @auth_token_required
    def get(self, data_key=None):
        data = []
        count = len(data)
        param = self._args['filter']

        query = self.get_table_query()
        if param is not None and param == 'notes':
            # Making filtering queries
            logger.debug("Build query '%s'" % param)

            if self._args['key'] is not None:
                query = self.get_filtered_notes(query, self._args['key'])
            else:
                query = self.get_all_notes(query)

        # Execute query
        count, data = self.execute_query(query, self._args['perpage'])
        # count, data = super().get(data_key)

        return self.response(data, elements=count)
