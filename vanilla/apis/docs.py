# -*- coding: utf-8 -*-

"""
Some endpoints implementation
"""

from __future__ import absolute_import

import rethinkdb as r
from rethinkdb.net import DefaultCursorEmpty
from flask_security import auth_token_required, roles_required
from flask_restful import reqparse
from confs import config
from ..services.rethink import schema_and_tables, BaseRethinkResource
from ..services.uploader import Uploader
from .. import decorators as deck
from commons import htmlcodes as hcodes
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
    def get(self, document_id=None):
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
        if document_id is not None:
            count, data = super().get(document_id)
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


#####################################
# A good tests for uploading images
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
                    index = 0
                    if len(tmp) > 1:
                        index = 1
                    sort = tmp[index]

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


##########################################
# Upload
##########################################
class RethinkUploader(Uploader, BaseRethinkResource):
    """ Uploading data and save it inside db """

    table = 'datadocs'
    ZOOMIFY_ENABLE = True

    @deck.apimethod
    def get(self, filename=None):
        return super(RethinkUploader, self).get(filename)

    @deck.apimethod
    def post(self):

        parser = reqparse.RequestParser()
# record=e0f7f651-b09a-4d0e-8b09-5f75dad7989e&flowChunkNumber=1&flowChunkSize=1048576&flowCurrentChunkSize=1367129&flowTotalSize=1367129&flowIdentifier=1367129-IMG_4364CR2jpg&flowFilename=IMG_4364.CR2.jpg&flowRelativePath=IMG_4364.CR2.jpg&flowTotalChunks=1

        # Handle record id, which is mandatory
        key = 'record'
        parser.add_argument(key, type=str)
        request_params = parser.parse_args()

        if key not in request_params or request_params[key] is None:
            return self.response(
                "No record to associate the image with",
                fail=True, code=hcodes.HTTP_DEFAULT_SERVICE_FAIL)
        id = request_params[key]

# // FEATURE REQUEST
# Try to create a decorator to parse arguments from the function args list
# // FEATURE REQUEST

        # Original upload
        obj, status = super(RethinkUploader, self).post()

        if isinstance(obj, dict) and 'filename' in obj['data']:
            myfile = obj['data']['filename']
            abs_file = self.absolute_upload_file(myfile)

            import os
            import re

            # Check exists
            if not os.path.exists(abs_file):
                return self.response(
                    "Failed to find the uploaded file",
                    fail=True, code=hcodes.HTTP_DEFAULT_SERVICE_FAIL)

            ftype = None
            fcharset = None
            try:
                # Check the type
                from plumbum.cmd import file
                out = file["-ib", abs_file]()
                tmp = out.split(';')
                ftype = tmp[0].strip()
                fcharset = tmp[1].split('=')[1].strip()
            except Exception:
                logger.warning("Unknown type for '%s'" % abs_file)

            # RethinkDB
            query = self.get_table_query()
            images = []
            action = self.insert

            # I should query the database to see if this record already exists
            # And has some images
            cursor = query.filter({'record': id})['images'].run()
            try:
                images = next(cursor)
                action = self.replace
            except DefaultCursorEmpty:
                pass

            # I could check if the filename is already there. But why? :)

            # Add the image to this record
            images.append({
                "code": re.sub(r"\.[^\.]+$", '', myfile),
                "filename": myfile,
                "filetype": ftype,
                "filecharset": fcharset})

            # Handle the file info insertion inside rethinkdb
            record = {
                "record": id,
                "images": images,
            }

            try:
                action(record)
                obj = {'id': id}
                logger.debug("Updated record '%s'" % id)
            except BaseException as e:
                return self.response(
                    str(e), fail=True, code=hcodes.HTTP_BAD_CONFLICT)

        return self.response(obj, code=status)
