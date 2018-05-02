
# B2STAGE HTTP-API for EUDAT project


| build | coverage | quality | uptime | swagger | feedback |
| --- | --- | --- | --- | --- | --- |
| [![Build Status](https://travis-ci.org/EUDAT-B2STAGE/http-api.svg?branch=master)](https://travis-ci.org/EUDAT-B2STAGE/http-api) | [![Coverage Status](https://coveralls.io/repos/github/EUDAT-B2STAGE/http-api/badge.svg?branch=master)](https://coveralls.io/github/EUDAT-B2STAGE/http-api?branch=master) | [![Code Health](https://landscape.io/github/EUDAT-B2STAGE/http-api/master/landscape.svg?style=flat)](https://landscape.io/github/EUDAT-B2STAGE/http-api/master) | [![Uptime Robot](https://img.shields.io/uptimerobot/ratio/m778586640-4e31f2b00e90bce508dcdf33.svg?maxAge=2592000)](https://stats.uptimerobot.com/xGG9gTK3q) | [![Swagger validation](https://img.shields.io/swagger/valid/2.0/https/b2stage-test.cineca.it/api/specs.svg)](http://petstore.swagger.io/?url=https://b2stage-test.cineca.it/api/specs&docExpansion=none) | [![Gitter](https://badges.gitter.im/EUDAT-B2STAGE/http-api.svg)](https://gitter.im/EUDAT-B2STAGE/http-api?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge) |


---


## Objectives

This project aims at developing a B2STAGE HTTP-API fot the EUDAT CDI.
The primary goal is to allow users to ingest and retrieve data via a standard RESTful HTTP interface in order to:

- hide the underlying technology from users,
- lower the entry barrier to using EUDAT services,
- simplify integration into existing workflows,
- allow direct access to data assets held with the EUDAT CDI.
<!--
Over the EUDAT2020 project other functionalities will be added: the development road map is available on the [EUDAT Wiki](https://confluence.csc.fi/display/EUDAT2/Service+building+roadmap)
-->


## Documentation

The first stable release is focused on the interaction with the `B2SAFE` service, allowing users to transfer and manage data on the `registered` **domain**.

### Get started

- try a [quick start](docs/quick_start.md)
- see the latest [webinar](https://pdonorio.github.io/chapters/webinars/b2stage)
- a demo [prototype](docs/prototype.md) of the current functionalities

### User guide

- [use](docs/user/user.md) an existing instance of the `HTTP-API`
- [main authentication](docs/user/authentication.md) based on `B2ACCESS`
- [alternative authentication](docs/user/authentication_b2safe.md) based on `B2SAFE`
- [endpoints](docs/user/endpoints.md) description and examples

### Administration

- read the [pre-requisites](docs/deploy/preq.md) prior to installation
- [startup](docs/deploy/startup.md) a working copy
- deploy in two [modes](docs/deploy/modes.md) 
- define the [authentication mechanism](docs/deploy/authentication.md) to be applied
- maintenance operations:
    + [debug](docs/deploy/debugging.md) the server operating on top of `B2SAFE` and fix eventual issues
    + keep your server [up-to-date](docs/deploy/updates.md)

### Development

- [add](docs/development/development.md) new features
- extra [operations](docs/development/operations.md)


## Implementation

This project is based on the open-source [RAPyDo framework](https://github.com/rapydo).

The API server is implemented with the latest Python 3 release using the Flask core. To facilitate and speed the development Docker is the base environment to automate the creation and configuration of the software stack needed.
The API interconnects with EUDAT services' native APIs or libraries.

To exchange data and metadata within the B2SAFE service (built on iRODS system as backend storage) the interface is implemented using (and contributing to) the official [python-irodsclient](https://github.com/irods/python-irodsclient).

NOTE: *the B2STAGE HTTP-API is an interface towards other EUDAT services which are subject to modifications and new developments, therefore the functionalities and the implementation will have to be changed accordingly*. 


## Copyright

Copyright 2011-2017 EUDAT CDI - www.eudat.eu
