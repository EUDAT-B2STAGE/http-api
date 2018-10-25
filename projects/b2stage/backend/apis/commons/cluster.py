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
BATCHES_DIR = seadata_vars.get('batch_dir')     # "batches"
ORDERS_DIR = seadata_vars.get('orders_dir')     # "orders"
PRODUCTION_DIR = seadata_vars.get('cloud_dir')  # "cloud"

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

        if self._handle is None:
            from b2stage.apis.services.rancher import Rancher
            params = self.load_credentials()
            # log.pp(params)
            self._handle = Rancher(**params)
        return self._handle

    def join_paths(self, paths):
        return str(path.build(paths))

    def get_ingestion_path(self, batch_id=None):
        paths = [self._handle._localpath]
        if batch_id is None:
            paths.append('batch')
        else:
            paths.append('ingestion')
            paths.append(batch_id)
        return str(path.build(paths))

    def mount_batch_volume(self, batch_id):
        host_path = self.get_ingestion_path(batch_id)
        container_fixed_path = self.get_ingestion_path()
        return "%s:%s" % (host_path, container_fixed_path)

    def get_input_zip_filename(self, filename=None, extension='zip', sep='.'):
        if filename is None:
            filename = 'input'
        else:
            filename = filename.replace('%s%s' % (sep, extension), '')
        return "%s%s%s" % (filename, sep, extension)


    '''
    Helper to construct a path of a data object
    inside irods.

    Note: Helper, only used inside this file.
    Note: The icom irods_client is of class
    IrodsPythonClient, defined in module
    rapydo/http-api/restapi/flask_ext/flask_irods/client
    '''
    def get_path_with_suffix(self, icom, mypath, suffix=None):
        paths = [mypath]
        if suffix is not None:
            paths.append(suffix)
        from utilities import path
        suffix_path = str(path.build(paths))
        return icom.get_current_zone(suffix=suffix_path)

    '''
    Return path of the batch inside irods, once the
    batch is in production.

    It consists of the irods zone (retrieved from
    the irods client object), the production batch
    directory (from config) and the batch_id if given.

    Example: /myIrodsZone/cloud/<batch_id>
    '''
    def get_production_path(self, icom, batch_id=None):
        return self.get_path_with_suffix(icom, PRODUCTION_DIR, batch_id)

    '''
    Return path of the batch inside irods, before
    the batch goes to production.

    It consists of the irods zone (retrieved from
    the irods client object), the ingestion batch
    directory (from config) and the batch_id if given.

    Example: /myIrodsZone/batches/<batch_id>
    '''
    def get_batch_path(self, icom, batch_id=None):
        return self.get_path_with_suffix(icom, BATCHES_DIR, batch_id)

    '''
    Return path of the order inside irods.

    It consists of the irods zone (retrieved from
    the irods client object), the order directory
    (from config) and the order_id if given.

    Example: /myIrodsZone/orders/<order_id>
    '''
    def get_order_path(self, icom, order_id=None):
        return self.get_path_with_suffix(icom, ORDERS_DIR, order_id)

    def get_batch_zipfile_path(self, batch_id, filename=None):
        container_fixed_path = self.get_ingestion_path()
        batch_file = self.get_input_zip_filename(filename)
        return str(path.build([container_fixed_path, batch_file]))

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
