# -*- coding: utf-8 -*-

"""
B2SAFE internal enpoint to manage metadata
"""

from __future__ import absolute_import

from commons.logs import get_logger
from commons.services.uuid import getUUID
from ..services.irods.client import IRODS_DEFAULT_USER
from ...base import ExtendedApiResource
from ... import decorators as decorate
from ....auth import authentication
from ....confs import config

logger = get_logger(__name__)


## // TO FIX:
# Use the correct irods user from the token,
# instad of IRODS_DEFAULT_USER
irods_tmp_user = IRODS_DEFAULT_USER


class MetaDataParser(ExtendedApiResource):

    @authentication.authorization_required(config.ROLE_INTERNAL)
    @decorate.apimethod
    def put(self, mid):

        # Get neo4j service object
        graph = self.global_get_service('neo4j')

        # Get filename and ipath from uuid using the graph
        try:
            de_node = graph.DigitalEntity.nodes.get(id=mid)
        except graph.DigitalEntity.DoesNotExist:
            return self.force_response(errors={mid: 'Not found.'})

        manifest_path = None
        manifest_path = self._recursive_search(de_node)

        if manifest_path is None:
            #except graph.DigitalEntity.DoesNotExist: # to be modified
            return self.force_response(errors={'manifest.xml not found.'})

        # Recursivly search for manifest.xml

        # Do irods things
        icom = self.global_get_service('irods', user=irods_tmp_user)

        # # irods paths
        # ipath = icom.get_irods_path(
        #     collection_node.path, de_node.filename)

        # 2. Find the manifest file
        # 3. Parse the manifest file

        ###########################
        # Models can be found inside the graphdb object

        # create a node
        myjson = {'test': 1, 'another': 99}
        node = graph.MetaData(content=myjson)
        # save it inside the graphdb
        node.save()

        # create a second node
        myid = getUUID()
        mylocation = 'irods:///%s' % myid
        datanode = graph.DigitalEntity(id=myid, location=mylocation)
        datanode.save()

        # connect the two nodes
        datanode.described.connect(node)
        print(node, datanode)

        return "Hello world"

    def _recursive_search(self, node):
        if node.collection:
            for de in node.parent.all():
                print(de.name)
                if de.name == 'manifest.xml':
                    print('manifest.xml found!')
                    return de.location
                else:
                    this._recursive_search(de)
        else:
            if de.name == 'manifest.xml':

                return de.location
            else:
                print('manifest.xml not found')
                return ''


    def _manifest_parser(self):
        pass
