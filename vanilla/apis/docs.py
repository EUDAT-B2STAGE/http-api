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
# Main resource
model = 'datavalues'
mylabel, mytemplate, myschema = schema_and_tables(model)


class Some(ExtendedApiResource, RDBquery):
    """ The json endpoint to rethinkdb class """

    schema = myschema
    template = mytemplate
    table = mylabel

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

    @deck.add_endpoint_parameter(name='filter', ptype=str)
    @deck.apimethod
    #@auth_token_required
    def get(self, data_key=None):
        """
        Obtain main data.
        Obtain single objects.
        Filter with predefined queries.
        """
        data = []
        count = 0
        limit = 10

        # Check arguments
        param = self._args['filter']
        if param is not None:
            # Making filtering queries
            logger.debug("Build query '%s'" % param)
            query = self.get_table_query()

            if param == 'autocompletion':
                query = self.get_autocomplete_data(
                    query, self._args['step'])

            # Execute query
            count, data = self.execute_query(query, limit)
        else:
            # Get all content from db
            count, data = self.get_content(data_key)

        # Wrap response, possibilities:
        # #return self.marshal(data, count)
        # #return self.nomarshal(data, count)
        # #return self.response(self._args)

        return self.nomarshal(data, count)

#############################################
# Should we move this to a generic resource?
    @auth_token_required
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

#############################################
