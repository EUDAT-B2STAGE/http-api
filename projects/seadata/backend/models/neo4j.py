# -*- coding: utf-8 -*-

"""
Graph DB abstraction from neo4j server.
These are custom models (project dependent).
"""

from __future__ import absolute_import
from neomodel import StringProperty, BooleanProperty, JSONProperty, \
    StructuredNode, StructuredRel, RelationshipTo, RelationshipFrom

from restapi.models.neo4j import User as UserBase

# from common.logs import get_logger
# logger = logging.get_logger(__name__)


class User(UserBase):
    """
    This class is a real 'Person'
    """
    name = StringProperty()
    surname = StringProperty()
    associated = RelationshipTo('IrodsUser', 'IS_ASSOCIATED_TO')

# ALTERNATIVE OVERRIDE:
# # Override existing
# setattr(User, 'name', StringProperty())
# setattr(User, 'surname', StringProperty())

## // TO FIX:
# should we consider roles?
    # _fields_to_show = {
    #     'role_1': ['name'],
    #     'role_2': ['name'],
    # }

##############################################################################
# MODELS
##############################################################################


## // TO FIX: connect IrodsUser to Authenticated user ?

class IrodsUser(StructuredNode):
    username = StringProperty(unique_index=True)
    default_user = BooleanProperty(default=True)
    ownership = RelationshipFrom('DigitalEntity', 'IS_OWNED_BY')
    associated = RelationshipFrom(User, 'IS_ASSOCIATED_TO')
    # hosted = RelationshipTo('Zone', 'IS_DEFINED_IN')


class Zone(StructuredNode):
    name = StringProperty(unique_index=True)
    hosting = RelationshipFrom('DigitalEntity', 'IS_LOCATED_IN')
    hosting_res = RelationshipFrom('Resource', 'IS_AVAILABLE_IN')
    # hosting_col = RelationshipFrom('Collection', 'IS_PLACED_IN')
    _fields_to_show = ['name']


class Resource(StructuredNode):
    name = StringProperty(unique_index=True)
    store = RelationshipFrom('DigitalEntity', 'STORED_IN')
    described = RelationshipFrom('MetaData', 'DESCRIBED_BY')
    hosted = RelationshipTo(Zone, 'IS_AVAILABLE_IN')
    _fields_to_show = ['name']


# class Collection(StructuredNode):
#     """ iRODS collection of data objects [Directory] """
#     id = StringProperty(required=True, unique_index=True)   # UUID
#     path = StringProperty(unique_index=True)
#     name = StringProperty()
#     belongs = RelationshipFrom('DigitalEntity', 'BELONGS_TO')
#     described = RelationshipFrom('MetaData', 'DESCRIBED_BY')
#     hosted = RelationshipTo(Zone, 'IS_PLACED_IN')
#     # A very strange relationship:
#     # Related to itself! A collection may be inside a collection.
#     matrioska_from = RelationshipFrom('Collection', 'INSIDE')
#     matrioska_to = RelationshipTo('Collection', 'INSIDE')
#     _fields_to_show = ['path', 'name']
#     _relationships_to_follow = ['belongs', 'hosted']


class Replication(StructuredRel):
    """
    Replica connects a DigitalEntity to its copies.
        Note: this is a relationship, not a node.
    """
    # Parent
    PPID = StringProperty()
    # Ancestor
    ROR = StringProperty()


class DigitalEntity(StructuredNode):
    """
    iRODS entity (file or collection)
    """
    id = StringProperty(required=True, unique_index=True)   # UUID
    location = StringProperty(index=True)
    # filename = StringProperty(index=True)
    # path = StringProperty()

    # collection is a DigitalEntity..
    collection = BooleanProperty(default=False)
    parent = RelationshipFrom('DigitalEntity', 'INSIDE')
    child = RelationshipTo('DigitalEntity', 'INSIDE')
    aggregation = RelationshipTo('Aggregation', 'BELONGS_TO')

    owned = RelationshipTo(IrodsUser, 'IS_OWNED_BY')
    located = RelationshipTo(Zone, 'IS_LOCATED_IN')
    stored = RelationshipTo(Resource, 'STORED_IN')

    replica = RelationshipTo(
        'DigitalEntity', 'IS_REPLICA_OF', model=Replication)
    master = RelationshipFrom(
        'DigitalEntity', 'IS_MASTER_OF', model=Replication)

    described = RelationshipFrom('MetaData', 'DESCRIBED_BY')
    identity = RelationshipFrom('PID', 'UNIQUELY_IDENTIFIED_BY')
    _fields_to_show = ['location']
    _relationships_to_follow = ['belonging', 'located', 'stored']


class PID(StructuredNode):
    """
    EUDAT Persistent Identification (PID)
    http://eudat.eu/User%20Documentation%20-%20PIDs%20in%20EUDAT.html
    """
    code = StringProperty(unique_index=True)
    checksum = StringProperty(index=True)   # For integrity
    described = RelationshipFrom('MetaData', 'DESCRIBED_BY')
    identify = RelationshipTo(DigitalEntity, 'UNIQUELY_IDENTIFIED_BY')


class MetaData(StructuredNode):
    """ Any metaData stored in any service level """

    # key = StringProperty(index=True)
    # metatype = StringProperty()         # Describe the level of metadata
    # value = StringProperty(index=True)

    content = JSONProperty()

    pid = RelationshipTo(PID, 'DESCRIBED_BY')
    data = RelationshipTo(DigitalEntity, 'DESCRIBED_BY')
    resource = RelationshipTo(Resource, 'DESCRIBED_BY')
    # collection = RelationshipTo(Collection, 'DESCRIBED_BY')


class Aggregation(StructuredNode):
    """ A generic relationship between nodes (data and metadata) """
    something = StringProperty()
    belonging = RelationshipFrom(DigitalEntity, 'BELONGS_TO')
