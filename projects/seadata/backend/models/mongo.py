# -*- coding: utf-8 -*-

""" Models for mongo database """

# from pymongo.write_concern import WriteConcern
from pymodm import MongoModel, fields


class Testing(MongoModel):
    onefield = fields.CharField()

    # NOTE: do not touch connection here, see experiments/mongo.py
    # class Meta:
    #     connection_alias = 'test'
    #     # write_concern = WriteConcern(j=True)

# FIXME: two fields are missing in ExternalAccounts
