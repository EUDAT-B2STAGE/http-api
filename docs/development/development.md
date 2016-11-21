## Pre-requisites
Before starting please make sure that you have installed on your system:

* [Docker](http://docs.docker.com/) 1.11+
* [docker-compose](https://docs.docker.com/compose/) 1.7+


##Coding Style
Primarily all code has to adhere to PEP8 http://legacy.python.org/dev/peps/pep-0008/.

## Quick start

If you need to jump in as soon as possible:

```bash
# Clone repo
git clone https://github.com/EUDAT-B2STAGE/http-api.git
# Init services
./do init
# Then run the final services
./do DEVELOPMENT
### Develop from here!

# You may also create another shell to mimic the API client
./do client_shell
/ # http GET http://apiserver/api/status

```

## Enable only the iRODS server

Note: if you want to use normal irods instead of B2safe service,
change the image name inside `docker-compose.yml`.

Then:

```bash
# Clone repo
git clone ...
# Init services
./do init
# Bring up only irods and postgres
docker-compose up -d icat
```