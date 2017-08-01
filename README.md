
# B2STAGE HTTP-API for EUDAT project


| build | coverage | quality | uptime | swagger |
| --- | --- | --- | --- | --- |
| [![Build Status](https://travis-ci.org/EUDAT-B2STAGE/http-api.svg)](https://travis-ci.org/EUDAT-B2STAGE/http-api) | [![Coverage Status](https://coveralls.io/repos/github/EUDAT-B2STAGE/http-api/badge.svg?branch=HEAD)](https://coveralls.io/github/EUDAT-B2STAGE/http-api?branch=HEAD) | [![Code Health](https://landscape.io/github/EUDAT-B2STAGE/http-api/master/landscape.svg?style=flat)](https://landscape.io/github/EUDAT-B2STAGE/http-api/master) | [![Uptime Robot](https://img.shields.io/uptimerobot/ratio/m778586640-4e31f2b00e90bce508dcdf33.svg?maxAge=2592000)](https://stats.uptimerobot.com/xGG9gTK3q) | [![Swagger validation](https://img.shields.io/swagger/valid/2.0/https/b2stage.cineca.it/api/specs.svg)](http://petstore.swagger.io/?url=https://b2stage.cineca.it/api/specs&docExpansion=none) |

NOTE: the B2STAGE HTTP-API is an interface towards other EUDAT services which are subject to modifications and new developments, therefore the functionalities and the implementation will have to be changed accordingly. 

Feedback on our first Release Candidate: [![Gitter](https://badges.gitter.im/EUDAT-B2STAGE/http-api.svg)](https://gitter.im/EUDAT-B2STAGE/http-api?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)


---


## Objectives

This project aims at developing a B2STAGE HTTP-API fot the EUDAT CDI.
The primary goal is to allow users to ingest and retrieve data via a standard RESTful HTTP interface in order to:

- hide the underlying technology from users,
- lower the entry barrier to using EUDAT services,
- simplify integration into existing workflows,
- allow direct access to data assets held with the EUDAT CDI.

The first development is focused on the interaction with B2SAFE, allowing users to transfer and manage data on the "registered" domain.
Over the EUDAT2020 project other functionalities will be added: the development road map is available on the [EUDAT Wiki](https://confluence.csc.fi/display/EUDAT2/Service+building+roadmap)


## Documentation

- [Quick start](docs/quick_start.md) for deploy and development

To be updated (not yet compatible with RC1):

- [User](docs/user/user.md) guide
- [Developer](docs/development/development.md) instructions
- [Deploy](docs/deploy/deploy.md) the server


## Implementation

This project is based on the open-source [RAPyDo framework](https://github.com/rapydo).

The API server is implemented with the latest Python 3 release using the Flask core. To facilitate and speed the development Docker is the base environment to automate the creation and configuration of the software stack needed.
The API interconnects with EUDAT services' native APIs or libraries.

To exchange data and metadata within the B2SAFE service (built on iRODS system as backend storage) the interface is implemented using the official [python-irodsclient](https://github.com/irods/python-irodsclient).

<!--
## quick notes

b2access basic endpoints:
https://eudat.eu/services/userdoc/b2access-service-integration#B2ACCESS_Services_Endpoints

https://eudat-aai.fz-juelich.de:8445/oauth-demo/get_token.jsp
-->
