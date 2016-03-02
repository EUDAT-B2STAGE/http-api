# -*- coding: utf-8 -*-

"""
Some endpoints implementation
"""

from __future__ import absolute_import

import rethinkdb as r
from flask.ext.security import auth_token_required, roles_required
from confs import config
from ..services.rethink import schema_and_tables, BaseRethinkResource
from .. import decorators as deck
from ... import get_logger

logger = get_logger(__name__)

#####################################
# Main resource
model = 'datavalues'
mylabel, mytemplate, myschema = schema_and_tables(model)


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

    def single_element(self, data, details='full'):
        """ If I request here one single document """
        single = []
        for steps in data.pop()['steps']:
            title = ""
            element = {}
            for row in steps['data']:
                if row['position'] == 1:
                    title = row['value']
                    if details != 'full':
                        break
                element[row['name']] = row['value']
            if details == 'full':
                single.insert(steps['step'], element)
            else:
                single.insert(steps['step'], title)
        return single

    def filter_nested_field(self, q, filter_value,
                            filter_position=None, field_name=None):
        """
        Filter a value nested by checking the field name also
        """
        mapped = q \
            .concat_map(
                lambda doc: doc['steps'].concat_map(
                    lambda step: step['data'].concat_map(
                        lambda data:
                            [{'record': doc['record'], 'step': data}])))

        logger.debug("Searching '%s' on pos '%s' or name '%s'" %
                     (filter_value, filter_position, field_name))
        if filter_position is not None:
            return mapped.filter(
                lambda doc: doc['step']['position'].eq(filter_position).
                and_(doc['step']['value'].eq(filter_value)))
        elif field_name is not None:
            return mapped.filter(
                lambda doc: doc['step']['name'].match(field_name).
                and_(doc['step']['value'].match(filter_value)))
        else:
            return q

    @deck.add_endpoint_parameter(name='filter', ptype=str)
    @deck.add_endpoint_parameter(name='step', ptype=int, default=1)
    @deck.add_endpoint_parameter(name='key')
    @deck.add_endpoint_parameter(name='details', default='short')
    @deck.apimethod
    @auth_token_required
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
            elif param == 'nested_filter' and self._args['key'] is not None:
                query = self.filter_nested_field(
                    query, self._args['key'], 1)

            # Execute query
            count, data = self.execute_query(query, self._args['perpage'])
        else:
            # Get all content from db
            count, data = super().get(data_key)
            # just one single ID - reshape!
            if data_key is not None:
                data = self.single_element(data, self._args['details'])

        return self.response(data, elements=count)

#####################################
# Keys for templates and submission
model = 'datakeys'
mylabel, mytemplate, myschema = schema_and_tables(model)


class RethinkDataKeys(BaseRethinkResource):
    """ Data keys administrable """

    schema = myschema
    template = mytemplate
    table = mylabel
    table_index = 'steps'

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
        if data_key is not None:
            count, data = super().get(data_key)
        else:
            count, data = self.execute_query(query, self._args['perpage'])

        return self.response(data, elements=count)

#####################################
# Keys for templates and submission
model = 'datadmins'
mylabel, mytemplate, myschema = schema_and_tables(model)


class RethinkDataForAdministrators(BaseRethinkResource):
    """ Data admins """

    schema = myschema
    template = mytemplate
    table = mylabel

    @deck.apimethod
    # @auth_token_required
    # @roles_required(config.ROLE_ADMIN)
    def get(self, id=None):
        count, data = super().get(id)
        return self.response(data, elements=count)

    @deck.apimethod
    @auth_token_required
    @roles_required(config.ROLE_ADMIN)
    def post(self):
        return super().post()

    @deck.apimethod
    @auth_token_required
    @roles_required(config.ROLE_ADMIN)
    def put(self, id):
        return super().put(id)

    @deck.apimethod
    @auth_token_required
    @roles_required(config.ROLE_ADMIN)
    def delete(self, id):
        return super().delete(id)


class RethinkImagesAssociations(BaseRethinkResource):
    """
    Fixing problems in images associations?
    """

    @deck.apimethod
    @auth_token_required
    def get(self, id=None):

        # Get the record value and the party name associated
        first = self.get_query().table('datavalues') \
            .concat_map(lambda doc: doc['steps'].concat_map(
                    lambda step: step['data'].concat_map(
                        lambda data: [{
                            'record': doc['record'], 'step': step['step'],
                            'pos': data['position'], 'party': data['value'],
                        }])
                )) \
            .filter({'step': 3, 'pos': 1}) \
            .pluck('record', 'party') \
            .group('party')['record'] \

        records_with_docs = list(
            self.get_query().table('datadocs')['record'].run())

        final = {}
        from operator import itemgetter

        for party, records in first.run().items():
            elements = set(records) - set(records_with_docs)
            if len(elements) > 0:
                # Remove the records containing the images
                ids = list(set(records) - set(records_with_docs))
                cursor = self.get_query().table('datavalues') \
                    .filter(lambda doc: r.expr(ids).contains(doc['record'])) \
                    .run()
                newrecord = []
                for obj in cursor:
                    val = obj['steps'][0]['data'][0]['value']
                    tmp = val.split('_')
                    sort = tmp[len(tmp)-1]
                    try:
                        sortme = int(sort)
                    except:
                        sortme = -1
                    newrecord.append({
                        'sortme': sortme,
                        'value': val,
                        'record': obj['record']
                    })
                final[party] = sorted(newrecord, key=itemgetter('sortme'))
                # final[party] = list(cursor)
        return self.response(final)

        # # Join the records with the uploaded files
        # second = first.eq_join(
        #     "record", r.table('datadocs'), index="record").zip()
        # # Group everything by party name
        # cursor = second.group('party').run(time_format="raw")
        # return self.response(cursor)
