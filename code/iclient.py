#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
Connecting to a remote icat (Eudat) server
"""

import os
import irods
from irods.session import iRODSSession

defaultZone = os.environ['IRODS_ZONE']

iconnection = {
    'host': os.environ['RODSERVER_ENV_IRODS_HOST'],
    'user': os.environ['IRODS_USER'],
    'password': os.environ['RODSERVER_ENV_IRODS_PASS'],
    'port': os.environ['RODSERVER_PORT_1247_TCP_PORT'],
    'zone': defaultZone
}
# print(iconnection)  # DEBUG
sess = iRODSSession(**iconnection)

try:
    coll = sess.collections.get("/" + defaultZone)
except irods.exception.NetworkException as e:
    print(str(e))
    exit(1)

print(coll.id)
print(coll.path)

for col in coll.subcollections:
    print col
for obj in coll.data_objects:
    print obj
