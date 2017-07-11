# -*- coding: utf-8 -*-

""" Models for mongo database """

from pymongo.write_concern import WriteConcern
from pymodm import MongoModel, fields

# NOTE: this db is already existing on an empty mongodb
MYDB = 'wfcat'


class Testing(MongoModel):
    onefield = fields.CharField()

    class Meta:
        connection_alias = MYDB
        # connection_alias = 'mytest'
        # write_concern = WriteConcern(j=True)

# FIXME: two fields are missing in ExternalAccounts


class wf_do(MongoModel):
    dc_identifier = fields.CharField()
    dc_title = fields.CharField()
    dc_subject = fields.CharField()
    dc_creator = fields.CharField()
    dc_contributor = fields.CharField()
    dc_publisher = fields.CharField()
    dc_type = fields.CharField()
    dc_format = fields.CharField()
    dc_date = fields.DateTimeField()
    dc_coverage_x = fields.FloatField()
    dc_coverage_y = fields.FloatField()
    dc_coverage_z = fields.FloatField()
    dc_coverage_t_min = fields.DateTimeField()
    dc_coverage_t_max = fields.DateTimeField()
    dcterms_available = fields.DateTimeField()
    dcterms_dateAccepted = fields.DateTimeField()
    dc_rights = fields.CharField()
    dcterms_isPartOf = fields.CharField()
    fileId = fields.CharField()

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = MYDB
