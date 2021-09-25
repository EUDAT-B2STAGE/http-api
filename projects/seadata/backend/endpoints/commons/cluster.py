from datetime import datetime
from pathlib import Path
from typing import Dict

from restapi.env import Env
from restapi.rest.definition import EndpointResource
from seadata.endpoints.commons.rancher import Rancher
from seadata.endpoints.commons.seadatacloud import seadata_vars

# from restapi.utilities.logs import log

DEFAULT_IMAGE_PREFIX = "docker"

"""
These are the names of the directories in the irods
zone for ingestion (i.e. pre-production) batches,
for production batches, and for orders being prepared.

They are being defined project_configuration.yml / .projectrc
"""
INGESTION_COLL = seadata_vars.get("ingestion_coll")  # "batches"
ORDERS_COLL = seadata_vars.get("orders_coll")  # "orders"
PRODUCTION_COLL = seadata_vars.get("production_coll")  # "cloud"
MOUNTPOINT = seadata_vars.get("resources_mountpoint")  # "/usr/share"

"""
These are the paths to the data on the hosts
that runs containers (both backend, celery and QC containers)
"""
INGESTION_DIR = seadata_vars.get("workspace_ingestion") or "batches"
ORDERS_DIR = seadata_vars.get("workspace_orders") or "orders"

"""
These are how the paths to the data on the host
are mounted into the containers.

Prepended before this is the RESOURCES_LOCALPATH,
defaulting to /usr/share.
"""

# THIS CANNOT CHANGE, otherwise QC containers will not work anymore!
FS_PATH_IN_CONTAINER = "/usr/share/batch"
# At least, the 'batch' part has to be like this, I am quite sure.
# About the '/usr/share', I am not sure, it might be read form some
# environmental variable passed to the container. But it is safe
# to leave it hard-coded like this.

CONTAINERS_VARS = Env.load_variables_group(prefix="containers")


class ClusterContainerEndpoint(EndpointResource):
    """
    Base to use rancher in many endpoints
    """

    _credentials: Dict[str, str] = {}

    def load_credentials(self):

        if not hasattr(self, "_credentials") or not self._credentials:
            self._credentials = Env.load_variables_group(prefix="resources")

        return self._credentials

    def get_or_create_handle(self):
        """
        Create a Rancher object and feed it with
        config that starts with "RESOURCES_",
        including the localpath, which is
        set to "/nfs/share".
        """

        params = self.load_credentials()
        return Rancher(**params)

    def get_ingestion_path_on_host(self, localpath: str, batch_id: str) -> str:
        """
        Return the path where the data is located
        on the Rancher host.

        The parts of the path can be configured,
        see: RESOURCES_LOCALPATH=/usr/share
        see: SEADATA_WORKSPACE_INGESTION=ingestion

        Example: /usr/share/ingestion/<batch_id>
        """

        return str(
            Path(
                localpath,  # "/usr/share" (default)
                INGESTION_DIR,  # "batches"  (default)
                batch_id,
            )
        )

    def get_ingestion_path_in_container(self):
        """
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
        """
        # "/usr/share/batch" (hard-coded)
        return str(Path(FS_PATH_IN_CONTAINER))

    def get_input_zip_filename(self, filename=None, extension="zip", sep="."):
        if filename is None:
            filename = "input"
        else:
            filename = filename.replace(f"{sep}{extension}", "")
        return f"{filename}{sep}{extension}"

    def get_irods_path(self, irods_client, mypath, suffix=None):
        """
        Helper to construct a path of a data object
        inside irods.

        Note: Helper, only used inside this file.
        Note: The irods_client is of class
        IrodsPythonClient, defined in module
        rapydo/http-api/restapi/connectors/irods/client
        """
        suffix_path = Path(mypath)
        if suffix:
            suffix_path.joinpath(suffix)

        return irods_client.get_current_zone(suffix=str(suffix_path))
        # TODO: Move to other module, has nothing to do with Rancher cluster!

    def get_irods_production_path(self, irods_client, batch_id=None):
        """
        Return path of the batch inside irods, once the
        batch is in production.

        It consists of the irods zone (retrieved from
        the irods client object), the production batch
        directory (from config) and the batch_id if given.

        Example: /myIrodsZone/cloud/<batch_id>
        """
        return self.get_irods_path(irods_client, PRODUCTION_COLL, batch_id)
        # TODO: Move to other module, has nothing to do with Rancher cluster!

    def get_irods_batch_path(self, irods_client, batch_id=None):
        """
        Return path of the batch inside irods, before
        the batch goes to production.

        It consists of the irods zone (retrieved from
        the irods client object), the ingestion batch
        directory (from config) and the batch_id if given.

        Example: /myIrodsZone/batches/<batch_id>
        """
        return self.get_irods_path(irods_client, INGESTION_COLL, batch_id)
        # TODO: Move to other module, has nothing to do with Rancher cluster!

    def get_irods_order_path(self, irods_client, order_id=None):
        """
        Return path of the order inside irods.

        It consists of the irods zone (retrieved from
        the irods client object), the order directory
        (from config) and the order_id if given.

        Example: /myIrodsZone/orders/<order_id>
        """
        return self.get_irods_path(irods_client, ORDERS_COLL, order_id)
        # TODO: Move to other module, has nothing to do with Rancher cluster!

    def return_async_id(self, request_id):
        # dt = "20170712T15:33:11"
        dt = datetime.strftime(datetime.now(), "%Y%m%dT%H:%M:%S")
        return self.response({"request_id": request_id, "datetime": dt})

    @staticmethod
    def get_container_name(batch_id, qc_name, qc_label=None):
        qc_name = (
            qc_name.replace("_", "").replace("-", "").replace(":", "").replace(".", "")
        )

        if qc_label is None:
            return f"{batch_id}_{qc_name}"

        return f"{batch_id}_{qc_label}_{qc_name}"

    @staticmethod
    def get_container_image(qc_name, prefix=None):
        if prefix is None:
            prefix = DEFAULT_IMAGE_PREFIX
        return f"{prefix}/{qc_name}"
