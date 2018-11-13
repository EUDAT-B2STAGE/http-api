# -*- coding: utf-8 -*-

from datetime import datetime
from restapi.rest.definition import EndpointResource
from b2stage.apis.commons.seadatacloud import seadata_vars
from restapi.services.detect import detector
from utilities import path
from utilities.logs import get_logger
log = get_logger(__name__)

DEFAULT_IMAGE_PREFIX = 'docker'

'''
These are the names of the directories in the irods
zone for ingestion (i.e. pre-production) batches,
for production batches, and for orders being prepared.

They are being defined in b2stage/confs/commons.yml,
which references config values defined in
b2stage/project_configuration.yml
'''
INGESTION_COLL = seadata_vars.get('ingestion_coll')    # "batches"
ORDERS_COLL = seadata_vars.get('orders_coll')          # "orders"
PRODUCTION_COLL = seadata_vars.get('production_coll')  # "cloud"
MOUNTPOINT = seadata_vars.get('resources_mountpoint')  # "/usr/share"

'''
These are the paths to the data on the hosts
that runs containers (both backend, celery and QC containers)
'''
INGESTION_DIR = seadata_vars.get('workspace_ingestion')    # "batches"
ORDERS_DIR = seadata_vars.get('workspace_orders')          # "orders"

'''
These are how the paths to the data on the host
are mounted into the containers.

Prepended before this is the RESOURCES_LOCALPATH,
defaulting to /usr/share.
'''

# THIS CANNOT CHANGE, otherwise QC containers will not work anymore!
FS_PATH_IN_CONTAINER = '/usr/share/batch'
# At least, the 'batch' part has to be like this, I am quite sure.
# About the '/usr/share', I am not sure, it might be read form some
# environmental variable passed to the container. But it is safe
# to leave it hard-coded like this.

CONTAINERS_VARS = detector.load_group(label='containers')


class ClusterContainerEndpoint(EndpointResource):
    """
    Base to use rancher in many endpoints
    """

    def custom_init(self):
        """ It gets called every time a new request is executed """
        self._handle = None
        self._credentials = {}
        # self.load_credentials()
        # self.get_or_create_handle()

    def load_credentials(self):

        if len(self._credentials) < 1:
            from restapi.services.detect import detector
            self._credentials = detector.load_group(label='resources')
        return self._credentials

    def get_or_create_handle(self):
        '''
        Create a Rancher object and feed it with
        config that starts with "RESOURCES_",
        including the localpath, which is
        set to "/nfs/share".
        '''

        if self._handle is None:
            from b2stage.apis.services.rancher import Rancher
            params = self.load_credentials()
            # log.pp(params)
            self._handle = Rancher(**params)
        return self._handle

    def join_paths(self, paths):
        return str(path.build(paths))

    def get_ingestion_path_on_host(self, batch_id):
        '''
        Return the path where the data is located
        on the Rancher host.

        The parts of the path can be configured,
        see: RESOURCES_LOCALPATH=/usr/share
        see: SEADATA_WORKSPACE_INGESTION=ingestion

        Example: /usr/share/ingestion/<batch_id>
        '''
        paths = [self._handle._localpath]      # "/usr/share" (default)
        paths.append(INGESTION_DIR)   # "batches"  (default)
        paths.append(batch_id)
        return str(path.build(paths))

    def get_ingestion_path_in_container(self):
        '''
        Return the path where the data is located
        mounted inside the Rancher containers.

        The start of the path can be configured,
        see: RESOURCES_LOCALPATH=/usr/local
        The directory name is fixed.

        Note: The batch_id is not part of the path,
        as every container only works on one batch
        anyway. With every batch being mounted into
        the same path, the programs inside the container
        can easily operate on whichever data is inside
        that directory.

        Example: /usr/share/batch/
        '''
        paths = [FS_PATH_IN_CONTAINER]    # "/usr/share/batch" (hard-coded)
        return str(path.build(paths))

    def get_input_zip_filename(self, filename=None, extension='zip', sep='.'):
        if filename is None:
            filename = 'input'
        else:
            filename = filename.replace('%s%s' % (sep, extension), '')
        return "%s%s%s" % (filename, sep, extension)

    def get_irods_path(self, irods_client, mypath, suffix=None):
        '''
        Helper to construct a path of a data object
        inside irods.

        Note: Helper, only used inside this file.
        Note: The irods_client is of class
        IrodsPythonClient, defined in module
        rapydo/http-api/restapi/flask_ext/flask_irods/client
        '''
        paths = [mypath]
        if suffix is not None:
            paths.append(suffix)
        from utilities import path
        suffix_path = str(path.build(paths))
        return irods_client.get_current_zone(suffix=suffix_path)
        # TODO: Move to other module, has nothing to do with Rancher cluster!

    def get_irods_production_path(self, irods_client, batch_id=None):
        '''
        Return path of the batch inside irods, once the
        batch is in production.

        It consists of the irods zone (retrieved from
        the irods client object), the production batch
        directory (from config) and the batch_id if given.

        Example: /myIrodsZone/cloud/<batch_id>
        '''
        return self.get_irods_path(irods_client, PRODUCTION_COLL, batch_id)
        # TODO: Move to other module, has nothing to do with Rancher cluster!

    def get_irods_batch_path(self, irods_client, batch_id=None):
        '''
        Return path of the batch inside irods, before
        the batch goes to production.

        It consists of the irods zone (retrieved from
        the irods client object), the ingestion batch
        directory (from config) and the batch_id if given.

        Example: /myIrodsZone/batches/<batch_id>
        '''
        return self.get_irods_path(irods_client, INGESTION_COLL, batch_id)
        # TODO: Move to other module, has nothing to do with Rancher cluster!

    def get_irods_order_path(self, irods_client, order_id=None):
        '''
        Return path of the order inside irods.

        It consists of the irods zone (retrieved from
        the irods client object), the order directory
        (from config) and the order_id if given.

        Example: /myIrodsZone/orders/<order_id>
        '''
        return self.get_irods_path(irods_client, ORDERS_COLL, order_id)
        # TODO: Move to other module, has nothing to do with Rancher cluster!

    def return_async_id(self, request_id):
        # dt = "20170712T15:33:11"
        dt = datetime.strftime(datetime.now(), '%Y%m%dT%H:%M:%S')
        return {'request_id': request_id, 'datetime': dt}

    @staticmethod
    def get_container_name(batch_id, qc_name):
        return '%s_%s' % (
            batch_id,
            qc_name
            .replace('_', '').replace('-', '')
            .replace(':', '').replace('.', '')
        )

    @staticmethod
    def get_container_image(qc_name, prefix=None):
        if prefix is None:
            prefix = DEFAULT_IMAGE_PREFIX
        return '%s/%s' % (prefix, qc_name)
