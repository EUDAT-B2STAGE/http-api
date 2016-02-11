#!/usr/bin/env python2
# -*- coding: utf-8 -*-
""" Graph DB """

import os
from restapi import get_logger

logger = get_logger(__name__)

# Parameters. To fix: take them from environment variables
PROTOCOL = 'http'
HOST = 'gdb'
PORT = '7474'
USER = 'neo4j'
PW = 'eudatapi'


##############################################################################
# GRAPHDB
##############################################################################

class MyGraph(object):
    """" A graph db neo4j instance """

    def __init__(self):
        super(MyGraph, self).__init__()
        self.connect()

    def connect(self):
        """ Connection http descriptor """
        try:
            os.environ["NEO4J_REST_URL"] = \
                PROTOCOL + "://" + USER + ":" + PW + "@" + \
                HOST + ":" + PORT + "/db/data"
            logger.info("Connected")
            print(os.environ["NEO4J_REST_URL"])
        except:
            raise EnvironmentError("Missing URL to connect to graph")
        # Set debug for cipher queries
        os.environ["NEOMODEL_CYPHER_DEBUG"] = "1"

    def cipher(self, query):
        """ Execute normal neo4j queries """
        from neomodel import db
        try:
            results, meta = db.cypher_query(query)
        except Exception as e:
            raise BaseException(
                "Failed to execute Cipher Query: %s\n%s" % (query, str(e)))
            return False
        logger.debug("Graph query. Res: %s\nMeta: %s" % (results, meta))
        return results

    def load_models(self, models=[]):
        """ Load models mapping Graph entities """

        for model in models:
            # Save attribute inside class with the same name
            logger.debug("Loading model '%s'" % model.__name__)
            setattr(self, model.__name__, model)

    def other(self):
        return self

# CREATE INSTANCE
migraph = MyGraph()


##############################################################################
# MODELS
##############################################################################

"""
VERY IMPORTANT!
Imports and models have to be defined/used AFTER normal Graphdb connection.
"""

from neomodel import StringProperty, \
    StructuredNode, StructuredRel, RelationshipTo, RelationshipFrom


class Person(StructuredNode):
    name = StringProperty(unique_index=True)
    ownership = RelationshipFrom('DataObject', 'IS_OWNED_BY')


class Zone(StructuredNode):
    name = StringProperty(unique_index=True)
    hosting = RelationshipFrom('DataObject', 'IS_LOCATED_IN')
    hosting_res = RelationshipFrom('Resource', 'IS_AVAILABLE_IN')
    hosting_col = RelationshipFrom('Collection', 'IS_PLACED_IN')


class Resource(StructuredNode):
    name = StringProperty(unique_index=True)
    store = RelationshipFrom('DataObject', 'STORED_IN')
    described = RelationshipFrom('MetaData', 'DESCRIBED_BY')
    hosted = RelationshipTo(Zone, 'IS_AVAILABLE_IN')


class Collection(StructuredNode):
    """ iRODS collection of data objects [Directory] """
    path = StringProperty(unique_index=True)
    name = StringProperty()
    belongs = RelationshipFrom('DataObject', 'BELONGS_TO')
    described = RelationshipFrom('MetaData', 'DESCRIBED_BY')
    hosted = RelationshipTo(Zone, 'IS_PLACED_IN')
    # Also Related to itself: a collection may be inside a collection.
    matrioska_from = RelationshipFrom('Collection', 'INSIDE')
    matrioska_to = RelationshipTo('Collection', 'INSIDE')


class Replication(StructuredRel):
    """
    Replica connects a DataObject to its copies.
        Note: this is a relationship, not a node.
    """
    # Parent
    PPID = StringProperty()
    # Ancestor
    ROR = StringProperty()


class DataObject(StructuredNode):
    """ iRODS data object [File] """
    location = StringProperty(unique_index=True)
    # PID = StringProperty(index=True)    # May not exist
    filename = StringProperty(index=True)
    path = StringProperty()
    owned = RelationshipTo(Person, 'IS_OWNED_BY')
    located = RelationshipTo(Zone, 'IS_LOCATED_IN')
    stored = RelationshipTo(Resource, 'STORED_IN')
    belonging = RelationshipTo(Collection, 'BELONGS_TO')
    replica = RelationshipTo('DataObject', 'IS_REPLICA_OF', model=Replication)
    described = RelationshipFrom('MetaData', 'DESCRIBED_BY')
    identity = RelationshipFrom('PID', 'UNIQUELY_IDENTIFIED_BY')


class PID(StructuredNode):
    """
    EUDAT Persistent Identification (PID)
    http://eudat.eu/User%20Documentation%20-%20PIDs%20in%20EUDAT.html
    """
    code = StringProperty(unique_index=True)
    checksum = StringProperty(index=True)   # For integrity
    described = RelationshipFrom('MetaData', 'DESCRIBED_BY')
    identify = RelationshipTo(DataObject, 'UNIQUELY_IDENTIFIED_BY')


class MetaData(StructuredNode):
    """ Any metaData stored in any service level """
    key = StringProperty(index=True)
    metatype = StringProperty()         # Describe the level of metadata
    value = StringProperty(index=True)
    pid = RelationshipTo(PID, 'DESCRIBED_BY')
    data = RelationshipTo(DataObject, 'DESCRIBED_BY')
    resource = RelationshipTo(Resource, 'DESCRIBED_BY')
    collection = RelationshipTo(Collection, 'DESCRIBED_BY')

ALL_GRAPH_MODELS = [
    Person, Zone, Resource,
    Collection, Replication, DataObject,
    PID, MetaData
]

migraph.load_models(ALL_GRAPH_MODELS)
