# -*- coding: utf-8 -*-

""" Models for mongo database """

# from pymongo.write_concern import WriteConcern
from pymodm import MongoModel, fields


class Testing(MongoModel):
    onefield = fields.CharField()

    class Meta:
        connection_alias = 'mytest'
        # write_concern = WriteConcern(j=True)
