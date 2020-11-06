"""
Communicating with docker via rancher

NOTE: to convert the output json and read it:
https://jsonformatter.curiousconcept.com/

API examples:
https://github.com/rancher/validation-tests/tree/master/tests/v2_validation/cattlevalidationtest/core
"""

import time

from restapi.utilities.logs import log
from seadata.endpoints.commons.cluster import CONTAINERS_VARS

# PERPAGE_LIMIT = 5
# PERPAGE_LIMIT = 50
PERPAGE_LIMIT = 1000


# Dev note:
# This object initialized in get_or_create_handle() in
# module "b2stage/backend/apis/commons/cluster.py".
# It receives all config that starts with "RESOURCES".
class Rancher:
    def __init__(
        self, key, secret, url, project, hub, hubuser, hubpass, localpath, qclabel
    ):

        ####################
        # SET URL
        self._url = url
        self._project = project
        # why? explained in http://bit.ly/2BBDJRj
        self._project_uri = f"{url}/projects/{project}/schemas"
        self._hub_uri = hub
        self._hub_credentials = (hubuser, hubpass)
        self._localpath = localpath  # default /nfs/share
        self._qclabel = qclabel
        self._hostlabel = "io.rancher.scheduler.affinity:host_label"

        ####################
        self.connect(key, secret)
        # self.project_handle(project)

    def connect(self, key, secret):
        import gdapi

        self._client = gdapi.Client(
            url=self._project_uri, access_key=key, secret_key=secret
        )

    # def project_handle(self, project):
    #     return self._client.by_id_project(self._project)

    def hosts(self):
        """
        'state':'active'
        'agentIpAddress':'130.186.13.150'
        'hostname':'sdc01'
        'driver':'openstack',
        'openstackConfig':{
            'username':'pdonorio'
        'info':{
            'osInfo':{
               'dockerVersion':'Docker version 1.13.1, build 092cba3',
               'kernelVersion':'4.4.0',
               'operatingSystem':'Ubuntu 16.04 LTS'
            'diskInfo':{
               'fileSystems':{
                  '/dev/vda1':{
                     'capacity':29715

            'cpuInfo':{
               'count':8,
            'memoryInfo':{
                'memFree':20287,
                'memTotal':24111,
            "physicalHostId":"1ph3",
        """
        hosts = {}
        for data in self._client.list_host():
            host = data.get("hostname")
            if not data.get("state") == "active":
                log.warning("Host {} not active", host)
                continue
            hosts[data.get("physicalHostId").replace("p", "")] = {
                "name": host,
                "ip": data.get("agentIpAddress"),
                "provider": data.get("driver"),
            }
        return hosts

    def obj_to_dict(self, obj):
        import json

        return json.loads(obj.__repr__().replace("'", '"'))

    def all_containers_available(self):
        """
        Handle paginations properly
        https://rancher.com/docs/rancher/v1.5/en/api/v2-beta/
        """

        is_all = False
        containers = []

        while not is_all:
            marker = len(containers)
            onepage = self._client.list_container(
                limit=PERPAGE_LIMIT, marker=f"m{marker}"
            )
            log.debug("Containers list marker: {}", marker)
            pagination = onepage.get("pagination", {})
            # print(pagination)
            is_all = not pagination.get("partial")
            for element in onepage:
                containers.append(element)

        return containers

    def containers(self):
        """
        https://github.com/rancher/gdapi-python/blob/master/gdapi.py#L68
        'io.rancher.container.system': 'true'
        """

        system_label = "io.rancher.container.system"

        containers = {}
        for info in self.all_containers_available():

            # detect system containers
            try:
                labels = self.obj_to_dict(info.get("labels", {}))
                if labels.get(system_label) is not None:
                    continue
            except BaseException:
                pass

            # labels = info.get('data', {}).get('fields', {}).get('labels', {})
            # info.get('externalId')
            name = info.get("name")
            cid = info.get("uuid")
            if cid is None:
                labels = info.get("labels", {})
                cid = labels.get("io.rancher.container.uuid", None)
            if cid is None:
                log.warning("Container {} launching", name)
                cid = name

            containers[cid] = {
                "name": name,
                "image": info.get("imageUuid"),
                "command": info.get("command"),
                "host": info.get("hostId"),
            }

        return containers

    def list(self):

        resources = {}
        containers = self.containers()
        ckey = "containers"

        for host_id, host_data in self.hosts().items():

            host_name = host_data.get("name")
            if ckey not in host_data:
                host_data[ckey] = {}

            for container_id, container_data in containers.items():
                if container_data.get("host") == host_id:
                    container_data.pop("host")
                    host_data["containers"][container_id] = container_data

            resources[host_name] = host_data

        return resources

    def recover_logs(self, container_name):
        import websocket as ws

        container = self.get_container_object(container_name)
        logs = container.logs(follow=False, lines=100)
        uri = logs.url + "?token=" + logs.token
        sock = ws.create_connection(uri, timeout=15)
        out = ""
        useless = "/bin/stty: 'standard input': Inappropriate ioctl for device"

        while True:
            try:
                line = sock.recv()
                if useless in line:
                    continue
            except ws.WebSocketConnectionClosedException:
                break
            else:
                out += line + "\n"

        return out

    def catalog_images(self):
        """ check if container image is there """
        catalog_url = f"https://{self._hub_uri}/v2/_catalog"
        # print(catalog_url)
        try:
            import requests

            r = requests.get(catalog_url, auth=self._hub_credentials)
            catalog = r.json()
            # print("TEST", catalog)
        except BaseException:
            return None
        else:
            return catalog.get("repositories", {})

    def internal_labels(self, pull=True):
        """
        Define Rancher docker labels
        """
        # to launch containers only on selected host(s)
        label_key = "host_type"
        label_value = self._qclabel

        obj = {self._hostlabel: f"{label_key}={label_value}"}

        if pull:
            # force to repull the image every time
            pull_label = "io.rancher.container.pull_image"
            obj[pull_label] = "always"

        return obj

    def run(
        self,
        container_name,
        image_name,
        wait_running=None,
        private=False,
        extras=None,
        wait_stopped=None,
        pull=True,
    ):

        ############
        if private:
            image_name_no_tags = image_name.split(":")[0]
            images_available = self.catalog_images()

            error = None
            if images_available is None:
                error = {"catalog": "Not reachable"}
            elif image_name_no_tags not in images_available:
                error = {"image": "Not found in our private catalog"}
            if error is not None:
                return {"error": error}

            # Add the prefix for private hub if it's there
            image_name = f"{self._hub_uri}/{image_name}"

        ############
        params = {
            "name": container_name,
            "imageUuid": "docker:" + image_name,
            "labels": self.internal_labels(pull),
            # entryPoint=['/bin/sh'],
            # command=['sleep', '1234567890'],
        }

        ############
        if extras is not None and isinstance(extras, dict):
            for key, value in extras.items():
                if key not in params:
                    # NOTE: this may print passwords, watch out!
                    params[key] = value

        ############
        from gdapi import ApiError

        try:
            container = self._client.create_container(**params)
        except ApiError as e:
            log.error("Rancher fail: {}", e.__dict__)
            return e.__dict__
        else:

            # Should we wait for the container?
            if wait_stopped is None:
                x = CONTAINERS_VARS.get("wait_stopped")
                wait_stopped = not (x.lower() == "false" or int(x) == 0)

            if wait_running is None:
                x = CONTAINERS_VARS.get("wait_running")
                wait_running = not (x.lower() == "false" or int(x) == 0)

            if wait_stopped or wait_running:
                log.info(
                    'Launched container {}" (external id: {})!',
                    container_name,
                    container.externalId,
                )

                # Wait for container to stop...
                while True:
                    co = self.get_container_object(container_name)
                    log.debug(
                        'Container {}": {} ({}, {}: {})',
                        container_name,
                        co.state,
                        co.transitioning,
                        co.transitioningMessage,
                        co.transitioningProgress,
                    )

                    # Add errors returned by rancher to the errors object:
                    if isinstance(co.transitioningMessage, str):
                        if "error" in co.transitioningMessage.lower():
                            error = {"container": co.transitioningMessage}

                        # Simplify life of first-time deployers:
                        if (
                            self._hub_uri in co.transitioningMessage
                            and "no basic auth credentials" in co.transitioningMessage
                        ):
                            log.error(
                                'Message from Rancher: "{}". Possibly you first need to add the registry on the Rancher installation!',
                                co.transitioningMessage,
                            )

                    # Stop loop based on container state:
                    if co.state == "error" or co.state == "erroring":
                        log.error("Error in container!")
                        error = {"container": co.transitioningMessage}
                        log.info("Detailed container info {}", co)
                        break
                    elif co.state == "stopped" and wait_stopped:
                        # even this does not guarantee success of operation inside container, of course!
                        log.info("Container has stopped!")
                        log.info("Detailed container info {}", co)
                        break
                    elif co.state == "running" and wait_running:
                        log.info("Container is running!")
                        if not not wait_stopped:
                            log.info("Detailed container info {}", co)
                            break

                    else:
                        time.sleep(1)

            # We will not wait for container to be created/running/stopped:
            else:
                log.info(
                    "Launched: {} (external id: {})!",
                    container_name,
                    container.externalId,
                )
            return None

    def get_container_object(self, container_name):
        containers = self.all_containers_available()
        # containers = self._client.list_container(limit=PERPAGE_LIMIT)

        # ####################################
        # # should I clean a little bit?
        # pagination = containers.get('pagination', {})
        # # print(pagination)
        # is_all = not pagination.get('partial')
        # if not is_all:
        #     log.warning('More pages...')

        ####################################
        for element in containers:

            # NOTE: container name is unique in the whole cluster env
            if element.name != container_name:
                continue

            # This patch does not work since Rancher is not able to
            # execute containers with same name, also if deployed
            # on different hosts. Also if verified here, the run will fail later"""
            # 'host_type=qc'
            # labels = element.labels

            # host_label = labels.get(self._hostlabel)

            # if host_label is not None:
            #     expected = self.internal_labels(pull=False).get(self._hostlabel)
            #     if host_label != expected:
            #         log.warning(
            #             "Found {} but deployed on {} (instead of {}). Skipping it",
            #             container_name, host_label, expected
            #         )
            #         continue

            return element

        return None

    def remove_container_by_name(self, container_name):
        obj = self.get_container_object(container_name)
        if obj is not None:
            self._client.delete(obj)
            return True
        else:
            log.warning("Did not found container: {}", container_name)
        return False

    def test(self):
        # client.list_host()
        # client.list_project()
        # client.list_service()
        pass
