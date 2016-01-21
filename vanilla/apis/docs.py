# -*- coding: utf-8 -*-

"""
Some endpoints implementation
"""

from __future__ import absolute_import
import os
import commentjson as json
from ..services.rethink import RDBquery, JSONS_PATH, JSONS_EXT
from ..base import ExtendedApiResource
from .. import decorators as deck
from flask.ext.security import auth_token_required  # , roles_required
from ...marshal import convert_to_marshal
# from ... import htmlcodes as hcodes
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

        # Check arguments
        logger.debug("Received args %s" % self._args)

        ###############################
        # Making filtering queries
        param = self._args['filter']
        if param is not None:
            logger.debug("Build a query from JSON '%s'" % param)
            #count, data = self.build_query(param)
        else:
            # Get all content from db
            (count, data) = self.get_content(data_key)

        # Wrap response
        #return self.marshal(data, count)
        return self.nomarshal(data, count)
        #return self.response(self._args)

    @auth_token_required
    def post(self):

        # Get JSON. The power of having a real object in our hand.
        json_data = request.get_json(force=True)
        return self.response(json_data)

    #     if 'query' in json_data and len(json_data) == 1:
    #         logger.debug("Build a query from JSON", json_data)
    #         count, data = self.build_query(json_data['query'])
    #         return self.nomarshal(data, count)

    #     ###############################
    #     # Otherwise INSERT ELEMENT
    #     else:
    #         valid = False
    #         for key, obj in json_data.items():
    #             if key in self.schema:
    #                 valid = True
    #         if not valid:
    #             return self.template, hcodes.HTTP_BAD_REQUEST

    #         # marshal_data = marshal(json_data, self.schema, envelope='data')
    #         myid = self.insert(json_data)

    #         # redirect to GET method of this same endpoint, with the id found
    #         address = url_for(self.table, data_key=myid)
    #         return redirect(address)
