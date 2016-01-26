
# REST API development for EUDAT project

This is an attempt to have a multi-container micro-services environment
to simulate some REST API service on top of an iCAT iRODS server.

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
git clone https://github.com/cineca-scai/docker-experiments.git
# Go into this directory
cd composers/irods
# Init services
docker-compose -f docker-compose.yml -f init.yml up icat
# When completed press CTRL-c
# Check volumes for persistence
docker volume ls
##DRIVER              VOLUME NAME
##local               sqldata
##local               irodsconf
##local               irodshome
##local               irodsresc
##local               eudathome

# ...and run the final services
docker-compose up -d iclient
docker exec -it irods_iclient_1 bash
root@icl:/code#

# Develop from here
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
4.1.6
```
