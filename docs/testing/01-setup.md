# B2STAGE HTTP API - Setting up a test instance

## 1. Synopsis
The B2STAGE HTTP API is an HTTP API for iRODS that takes the specific metadata and data structures into account that are created 
by B2SAFE. In that sense it is not a general HTTP API to any iRODS instance and any data in iRODS.

**The service is still under development**, hence the instructions provided here might still change.

The API is deployed using Docker images and comes in two modes. 
The *debug* mode deployes the HTTP API framework and an extra iRODS instance that is enabled with B2SAFE. 
Here the API is directly tied to the iRODS instance inside of Docker. You can access the API and iRODS by username/password.

The *production* mode deploys the HTTP API and generates certificates.(*Note: what kind of certificates? Server certificates?*)
In the setup you need to provide an own iRODS instance. Since in production mode the HTTP API uses B2ACCESS to retrieve all user 
information, your iRODS instance also needs to be coupled to B2ACCESS for user management.
The iRODS instance needs to be enabled with the latest B2SAFE version v4.

## 2. Setting up the docker environment and test instance
### Install docker 
```sh
wget -qO- https://get.docker.com/ | sh
sudo usermod -aG docker $(whoami)
sudo apt-get install python3-pip
sudo pip3 install docker-compose
```

Check Docker

```sh
docker run hello-world
```

*Note: Will that still be needed with the new install scripts?*

### Install dependencies

```sh 
sudo apt-get install git
```

### Install *rapydo*
*Note: Do we have a registry and description for all the docker images?*

- What is rapydo?
- Why is it used here?
- Why Docker?

The general installation guide can be found [here](https://github.com/EUDAT-B2STAGE/http-api/blob/master/docs/quick_start.md).
*Note: Adjust with release when it is out.*

General steps to start fresh:
```sh
git clone https://github.com/EUDAT-B2STAGE/http-api.git
cd http-api
git checkout 0.5.2 # adjust o branch
```
Install rapydo
```sh
sudo data/scripts/prerequisites.sh
rapydo init
rapydo start
rapydo shell backend --command 'restapi launch' &
```
You should now be able to access the REST API endpoint on that machine:

`http://<fqdn or localhost>:8080/api/status`

Enable the Swagger endpoint:
```sh
rapydo interfaces swagger &
```

Access the endpoint:

```sh
http://<fqdn or localhost>/swagger-ui/?url=http://<fqdn or localhost>:8080/api/specs
```

### Installing B2SAFE and a replication event hook

The HTTP API is designed to interact with data that is subject to the B2SAFE data policies, i.e. data that carries a PID and certain links to replicas or parent data.

To attach PIDs and simulate the replication we need to install the B2SAFE module in the Docker iRODS instance and put an event hook in place that automatically triggeres a replication from a collection _/$rodsZoneClient/home/*/b2safe/_ to _/$rodsZoneClient/home/$userNameClient/b2replication_.

1. Get a shell on the iRODS server, by default you are root. You can change to become the irods user.
 ```sh
 rapydo shell icat
 berods
 cd
 ```
2. Install [B2SAFE](https://github.com/EUDAT-Training/B2SAFE-B2STAGE-Training/blob/master/03-install-B2SAFE.md)
- Check out the latest version of B2SAFE
	```sh
	git clone https://github.com/EUDAT-B2SAFE/B2SAFE-core.git
	cd ~/B2SAFE-core/packaging
	./create_deb_package.sh
	exit
	```
- Install the package as *root*:
  ```sh
  dpkg -i /var/lib/irods/debbuild/irods-eudat-b2safe_4.0-1.deb
  ```
- Configure B2SAFE (as user *irods*):
  Before proceeding copy the Handle certificates over to the docer image. You will need a *certificate_only.pem* and the corresponding *privkey.pem*. Make sure the user *irods* has access rights to these two files.
  ```sh
  berods
  vi /opt/eudat/b2safe/packaging/install.conf
  ```
  Adjust 
  ```sh
  SERVER_ID="irods://<fqdn>:1247"
  HANDLE_SERVER_URL="https://epic4.storage.surfsara.nl:8007"
  PRIVATE_KEY="/var/lib/irods/privkey.pem"
  CERTIFICATE_ONLY="/var/lib/irods/certificate_only.pem"
  PREFIX="<PREFIX>"
  HANDLEOWNER="200:0.NA/$PREFIX"
  REVERSELOOKUP_USERNAME="<PREFIX>"
  HTTPS_VERIFY="False"
  MSIFREE_ENABLED=false
  ```
  Configure and install B2SAFE:
  ```sh
  source /etc/irods/service_account.config
  cd /opt/eudat/b2safe/packaging/
  ./install.sh
  exit
  ```
- As *root* install missing python packages and the B2HANDLE library:
  ```sh
  apt-get install python-pip
  pip install queuelib dweepy 
  apt-get install python-lxml python-defusedxml python-httplib2 python-simplejson
  ```
  ```sh
  git clone https://github.com/EUDAT-B2SAFE/B2HANDLE
  cd B2HANDLE/
  python setup.py bdist_egg
  cd dist/
  easy_install b2handle-*.egg
  ```
- Test B2HANDLE (as user *irods*)
  ```sh
  berods
  cd
  /opt/eudat/b2safe/cmd/epicclient2.py \
  os /opt/eudat/b2safe/conf/credentials \
  create www.test.com
  
  cd B2SAFE-core
  irule -F rules/eudatRepl_coll.r
  ```
- Test the B2SAFE replication. The replication rule will only work when the iRODS hosts file */etc/irods/hosts_config.json* is set up correctly:
  ```sh
  {
     "schema_name": "hosts_config",
     "schema_version": "v3",
     "host_entries": [
         {
             "address_type" : "local",
             "addresses" : [
                    {"address" : "<fqdn>"}
              ]
         }
      ]
   }
  ```
  
  Restart the iRODS server as root
  ```sh
  exit
  service irods restart
  berods
  ```
  
  Remove the previously created collection and run the B2SAFE replication again:
  ```sh
  irm -r t_coll
  irmtrash
  irule -F rules/eudatRepl_coll.r
  ``` 
 
3. Install event hook
 ```sh
 vim /etc/irods/core.re
 ``` 
 Insert 
 ```sh
 acPostProcForPut {
    	ON($objPath like "/$rodsZoneClient/home/$userNameClient/b2safe/*"){
        	writeLine("serverLog","DEBUG replication to
            	/$rodsZoneClient/home/$userNameClient/b2replication");
        	EUDATReplication("/$rodsZoneClient/home/$userNameClient/b2safe",
            	"/$rodsZoneClient/home/$userNameClient/b2replication",
            	"true", "true", *response);
    	}
 }
 ```

4. To see whether the eventhook works, open a new shell:
 ```sh
 rapydo shell icat
 tail -f /var/lib/irods/log/rodsLog.<DATE>
 ```
## 3. Update of the test environment
The HTTP API is denpending on the rapydo framework. Hence, when the HTTP API code base is updated the rapydo framework has to be updated too to the corresponding rapydo version.
In the [project_configuration.yaml](https://github.com/EUDAT-B2STAGE/http-api/blob/0.6.0/projects/eudat/project_configuration.yaml) you will find a section that specifies which HTTP API version works with which rapydo version.
The rapydo codebase is installed in a folder *~/http-api/submodules*.
To update your current HTTP API do the following:

1. Clean all docker images
 ```sh
 rapydo clean --rm-volumes
 ```
2. Remove the old code for rapydo in the *submodules* folder
 ```sh
 rm -r submodules/* -f
 ```
3. Pull the git repository and switch to the branch you would like to install (e.g. version 0.6.0)
 ```sh
 git pull
 git checkout 0.6.0
 git branch
 ```
4. Reinstall all docker images with the correct code base and start rapydo
 ```sh
 rapydo init
 rapydo start
 ```
 To check whether the correct rapydo version is associated to the HTTP API you can check the current rapydo version with
 ```sh
 cd http-api/submodules/backend
 git branch -a
 ```
 and copmare with the version that is required in either the */http-api/projects/eudat/project_configuration.yaml* or the *requirements.txt*.

5. Launch the HTTP API and the swagger endpoints
 ```sh
 rapydo shell backend --command 'restapi launch' &
 rapydo interfaces swagger &
 ```

