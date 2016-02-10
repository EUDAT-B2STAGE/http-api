
# REST API development for EUDAT project

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
git clone ...
# Init services
scripts/run.sh init
# Then run the final services
scripts/run.sh
# Open the client to test code or run the API server
docker exec -it irods_iclient_1 bash
root@icl:/code#
### Develop from here!
```

## Documentation

For a more detailed explanation and some deep understanding:

* [Preparing the environment](docs/preparation.md)
* [Running the services](docs/running.md)
* [Developing](docs/client.md)
* [Admin operations](docs/admin.md)

## Versions

```
irods@rodserver:~$ apt-cache showpkg irods-icat
Package: irods-icat
Versions:
4.1.7
```
