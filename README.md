
# REST API development for EUDAT project

[![Build Status](https://travis-ci.org/EUDAT-B2STAGE/http-api.svg)](https://travis-ci.org/EUDAT-B2STAGE/http-api)

This is an attempt to have a multi-container micro-services environment
to develop REST API service on top of an iCAT iRODS server.

*WARNING*: this environemnt is in an early stage of development.
You should expect things not to work.

--

## Pre-requisites

Before starting please make sure that you have installed on your system:

* [Docker](http://docs.docker.com/) 1.11+
* [docker-compose](https://docs.docker.com/compose/) 1.7+

## Quick start

If you need to jump in as soon as possible:

```bash
# Clone repo
git clone https://github.com/EUDAT-B2STAGE/http-api.git
# Init services
./do init
# Then run the final services
./do DEVELOPMENT
### Develop from here!

# You may also create another shell to mimic the API client
./do client_shell
/ # http GET http://apiserver/api/status

```

## Enable only the iRODS server

Note: if you want to use normal irods instead of B2safe service,
change the image name inside `docker-compose.yml`.

Then:

```bash
# Clone repo
git clone ...
# Init services
./do init
# Bring up only irods and postgres
docker-compose up -d icat
```

## Documentation

For a more detailed explanation and some deep understanding:

** WARNING: the following pages are not yet updated **

* [Preparing the environment](docs/preparation.md)
* [Running the services](docs/running.md)
* [Developing](docs/client.md)
* [Admin operations](docs/admin.md)

## Versions

```
$ ./do irods_shell

irods@rodserver:~$ apt-cache showpkg irods-icat | grep -i versions -A 1
Versions:
4.1.8 (/var/lib/dpkg/status)
```
