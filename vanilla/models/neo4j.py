# -*- coding: utf-8 -*-

"""
Graph DB abstraction from neo4j server.
These are custom models!

VERY IMPORTANT!
Imports and models have to be defined/used AFTER normal Graphdb connection.
"""

from __future__ import absolute_import
from neomodel import StringProperty, \
    StructuredNode, StructuredRel, RelationshipTo, RelationshipFrom

from ..neo4j import User as UserBase

# from common.logs import get_logger
# logger = logging.get_logger(__name__)


class User(UserBase):
    name = StringProperty()
    surname = StringProperty()

# OR ?
# # Override existing
# setattr(User, 'name', StringProperty())
# setattr(User, 'surname', StringProperty())

##############################################################################
# MODELS
##############################################################################


## // TO FIX: connect Person to Authenticated user ?

class Person(StructuredNode):
    name = StringProperty(unique_index=True)
    ownership = RelationshipFrom('DataObject', 'IS_OWNED_BY')


class Zone(StructuredNode):
    name = StringProperty(unique_index=True)
    hosting = RelationshipFrom('DataObject', 'IS_LOCATED_IN')
    hosting_res = RelationshipFrom('Resource', 'IS_AVAILABLE_IN')
    hosting_col = RelationshipFrom('Collection', 'IS_PLACED_IN')
    _fields_to_show = ['name']

## // TO FIX:
# should we consider roles?
    # _fields_to_show = {
    #     'role_1': ['name'],
    #     'role_2': ['name'],
    # }


class Resource(StructuredNode):
    name = StringProperty(unique_index=True)
    store = RelationshipFrom('DataObject', 'STORED_IN')
    described = RelationshipFrom('MetaData', 'DESCRIBED_BY')
    hosted = RelationshipTo(Zone, 'IS_AVAILABLE_IN')
    _fields_to_show = ['name']


class Collection(StructuredNode):
    """ iRODS collection of data objects [Directory] """
    id = StringProperty(required=True, unique_index=True)   # UUID
    path = StringProperty(unique_index=True)
    name = StringProperty()
    belongs = RelationshipFrom('DataObject', 'BELONGS_TO')
    described = RelationshipFrom('MetaData', 'DESCRIBED_BY')
    hosted = RelationshipTo(Zone, 'IS_PLACED_IN')
    # A very strange relationship:
    # Related to itself! A collection may be inside a collection.
    matrioska_from = RelationshipFrom('Collection', 'INSIDE')
    matrioska_to = RelationshipTo('Collection', 'INSIDE')
    _fields_to_show = ['path', 'name']
    _relationships_to_follow = ['belongs', 'hosted']


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
    """
    iRODS data object [File]
    """
    id = StringProperty(required=True, unique_index=True)   # UUID
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
    _fields_to_show = ['location', 'filename', 'path']
    _relationships_to_follow = ['belonging', 'located', 'stored']


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
