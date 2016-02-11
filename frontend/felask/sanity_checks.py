# -*- coding: utf-8 -*-

""" SQLalchemy sanity checks """

import logging

from sqlalchemy import inspect
from sqlalchemy.ext.declarative.clsregistry import _ModuleMarker
from sqlalchemy.orm import RelationshipProperty

logger = logging.getLogger(__name__)

def is_sane_database(Base, session):
    """Check whether the current database matches the models declared in model base.

    Currently we check that all tables exist with all columns. What is not checked
    * Column types are not verified
    * Relationships are not verified at all (TODO)

    :param Base: Declarative Base for SQLAlchemy models to check
    :param session: SQLAlchemy session bound to an engine
    :return: True if all declared models have corresponding tables and columns.
    """

    engine = session.get_bind()
    iengine = inspect(engine)
    errors = False
    tables = iengine.get_table_names()

    import re
    myre = re.compile(r'[A-Z]+\(?[0-9]*\)?')

    # Go through all SQLAlchemy models
    for name, klass in Base._decl_class_registry.items():

        if isinstance(klass, _ModuleMarker):
            # Not a model
            continue

        table = klass.__tablename__
        if table in tables:
            # Check all columns are found
            # Looks like [{'default': "nextval('sanity_check_test_id_seq'::regclass)", 'autoincrement': True, 'nullable': False, 'type': INTEGER(), 'name': 'id'}]

            columns = []
            coltypes = {}
            for col in iengine.get_columns(table):
                name = col['name']
                columns.append(name)
                coltypes[name] = col['type']
            #print(columns, coltypes)
            mapper = inspect(klass)

            for column_prop in mapper.attrs:
                if isinstance(column_prop, RelationshipProperty):
                    # TODO: Add sanity checks for relations
                    pass
                else:
                    for column in column_prop.columns:
                        # Assume normal flat column
                        if not column.key in columns:
                            logger.error("Model %s declares column %s which does not exist in database %s", klass, column.key, engine)
                            errors = True
                        else:
                            # Check types
                            dbcol = str(column.type)
                            schemacol = str(coltypes[column.key])

                            # Skip case of enums with specific name is an exception
                            if myre.search(schemacol) and schemacol != dbcol:
                                #print(str(column.type), str(coltypes[column.key]))
                                logger.error("Different column '%s'! schema is %s, table has %s." % \
                                    (column, column.type, coltypes[column.key]))

        else:
            logger.error("Model %s declares table %s which does not exist in database %s", klass, table, engine)
            errors = True

    return not errors
