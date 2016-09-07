# -*- coding: utf-8 -*-

"""
B2SAFE internal enpoint to manage metadata
"""

from __future__ import absolute_import

from commons.logs import get_logger
from commons.services.uuid import getUUID
from ...services.irods.client import IRODS_DEFAULT_USER
from ...base import ExtendedApiResource
from ... import decorators as decorate
from ....auth import authentication
from ....confs import config

logger = get_logger(__name__)

irods_tmp_user = IRODS_DEFAULT_USER


## // TO FIX:
# Use the correct irods user from the token,
# instad of IRODS_DEFAULT_USER
irods_tmp_user = IRODS_DEFAULT_USER


class MetaDataParser(ExtendedApiResource):

    @authentication.authorization_required(config.ROLE_INTERNAL)
    @decorate.apimethod
    def put(self, mid=None):
        # Get neo4j service object
        graph = self.global_get_service('neo4j')

        # Do irods things
        # icom = self.global_get_service('irods', user=irods_tmp_user)

        # create a test node
        # myid = getUUID()
        # mylocation = 'irods:////tempZone/home/rods'
        # datanode = graph.DigitalEntity(id=myid, location=mylocation,
        #     filename = 'manifest.xml')
        # datanode.save()

        # Get the manifest.xml using the graph

        try:
            de_node = graph.DigitalEntity.nodes.get(id=mid)
        except graph.DigitalEntity.DoesNotExist:

            logger.info("Insed MetaDataParser: %s", mid)
            return self.force_response(errors={mid: 'Not found.'})

        manifest_path = None
        manifest_path = self._recursive_search(de_node)

        if manifest_path is None:
            # except graph.DigitalEntity.DoesNotExist: # to be modified
            return self.force_response(errors={'manifest.xml not found.'})
        else:
            logger.info("Manifest.xml found in %s", manifest_path)

        # 3. Parse the manifest file
        return "Hello world"

    def _recursive_search(self, node):
        if node.collection:
            for de in node.parent.all():
                logger.info(de.filename)
                if de.filename == 'manifest.xml':
                    logger.info('manifest.xml found!')
                    return de.location
                else:
                    self._recursive_search(de)
        else:
            if node.filename == 'manifest.xml':
                return node.location
            else:
                logger.info('manifest.xml not found')
                return None


    def _manifest_parser(self):
        pass
