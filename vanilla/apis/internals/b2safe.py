# -*- coding: utf-8 -*-

"""
B2SAFE internal service operations
served as HTTP REST API endpoints.
"""

from __future__ import absolute_import

from commons.logs import get_logger
from commons.services.uuid import getUUID
from ...base import ExtendedApiResource
from ... import decorators as decorate
from ....auth import auth

logger = get_logger(__name__)


class MetadataObject(ExtendedApiResource):

    @auth.login_required
    # @decorate.add_endpoint_parameter("location", required=True)
    @decorate.apimethod
    def post(self):
        """ Register a UUID """

        # Create graph object
        graph = self.global_get_service('neo4j')

        #######################
        # User
        userobj = self.get_current_user()
        irodsusers = userobj.associated.search(default_user=True)

        myuser = None
        if len(irodsusers) < 1:
# // TO FIX:
# explore association from existing irods user
            # associate with guest user
            class myuser(object):
                username = 'guest'
            print("MY USER", myuser)
        else:
            myuser = irodsusers.pop()

        myuserobj = None
        try:
            myuserobj = graph.IrodsUser.nodes.get(username=myuser.username)
        except graph.IrodsUser.DoesNotExist:
            return self.response(errors={
                'iRODS user':
                    'no valid account associated on the iRODS server'})

        #######################
        # Create UUID
        myid = getUUID()
# // TO FIX:
# to be requested
        mylocation = 'noprotocol://TOBEDEFINED/%s/%s/UNKNOWN' % (myuser, myid)
        dobj = graph.DataObject(id=myid, location=mylocation)
        dobj.save()

        #######################
        # Link the obj
        dobj.owned.connect(myuserobj)

        #######################
        # Return the UUID
        return dobj.id
