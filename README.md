
# REST API development for EUDAT project

[![Build Status](https://travis-ci.org/EUDAT-B2STAGE/http-api.svg?branch=master)](https://travis-ci.org/EUDAT-B2STAGE/http-api.svg?branch=master)

This is an attempt to have a multi-container micro-services environment
to develop REST API service on top of an iCAT iRODS server.

*WARNING*: this environemnt is in an early stage of development.
You should expect things not to work.

--

## Pre-requisites

Before starting please make sure that you have installed on your system:

* [Docker](http://docs.docker.com/) 1.9+
* [docker-compose](https://docs.docker.com/compose/) 1.5+

## Quick start

If you need to jump in as soon as possible:

```bash
# Clone repo
git clone https://github.com/EUDAT-B2STAGE/http-api.git
# Init services
scripts/run.sh init
# Then run the final services
scripts/run.sh graceful
# Open the client to test code or run the API server
scripts/run.sh server_shell
root@api:/code/project# ./boot devel
### Develop from here!

# You may also create another shell to mimic the API client
scripts/run.sh client_shell
/ # http GET http://api:5000/api/verify

```

## Enable only irods server

Note: if you want to use normal irods instead of B2safe service,
change the image name inside `docker-compose.yml`.

Then:

```bash
# Clone repo
git clone ...
# Init services
scripts/run.sh init
# Bring up only irods and postgres
docker-compose up -d icat
```

## Documentation

For a more detailed explanation and some deep understanding:

** WARNING: the following links must be updated **

* [Preparing the environment](docs/preparation.md)
* [Running the services](docs/running.md)
* [Developing](docs/client.md)
* [Admin operations](docs/admin.md)

## Versions

```
$ docker exec -it httpapi_icat_1 bash

irods@rodserver:~$ apt-cache showpkg irods-icat
Package: irods-icat
Versions:
4.1.8
```
