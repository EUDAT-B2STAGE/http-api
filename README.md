# B2STAGE HTTP-API for EUDAT project

[![Build Status](https://travis-ci.com/EUDAT-B2STAGE/http-api.svg?branch=1.1.2)](https://travis-ci.com/EUDAT-B2STAGE/http-api) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/3d59eae46ec040008a99116396229dff)](https://www.codacy.com/app/EUDAT/http-api?utm_source=github.com&utm_medium=referral&utm_content=EUDAT-B2STAGE/http-api&utm_campaign=Badge_Grade)

---

## Objectives

This project aims at developing a B2STAGE HTTP-API fot the EUDAT CDI.
The primary goal is to allow users to ingest and retrieve data via a standard RESTful HTTP interface in order to:

- hide the underlying technology from users,
- lower the entry barrier to using EUDAT services,
- simplify integration into existing workflows,
- allow direct access to data assets held with the EUDAT CDI.

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
- [debug](docs/deploy/debugging.md) the server operating on top of `B2SAFE` and fix eventual issues
- keep your server [up-to-date](docs/deploy/updates.md)

### Development

- [add](docs/development/development.md) new features
- extra [operations](docs/development/operations.md)

## Implementation

This project is based on the open-source [RAPyDo framework](https://github.com/rapydo).

The API server is implemented with the latest Python 3 release using the Flask core. To facilitate and speed the development Docker is the base environment to automate the creation and configuration of the software stack needed.
The API interconnects with EUDAT services' native APIs or libraries.

To exchange data and metadata within the B2SAFE service (built on iRODS system as backend storage) the interface is implemented using (and contributing to) the official [python-irodsclient](https://github.com/irods/python-irodsclient).

NOTE: _the B2STAGE HTTP-API is an interface towards other EUDAT services which are subject to modifications and new developments, therefore the functionalities and the implementation will have to be changed accordingly_.

## Acknowledgement

This work is co-funded by the [EOSC-hub project](http://eosc-hub.eu/) (Horizon 2020) under Grant number 777536.
<img src="https://wiki.eosc-hub.eu/download/attachments/1867786/eu%20logo.jpeg?version=1&modificationDate=1459256840098&api=v2" height="24">
<img src="https://wiki.eosc-hub.eu/download/attachments/18973612/eosc-hub-web.png?version=1&modificationDate=1516099993132&api=v2" height="24">

## Copyright

Copyright 2011-2020 EUDAT CDI - www.eudat.eu
