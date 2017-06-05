
# B2STAGE HTTP-API for EUDAT project

[![Build Status](https://travis-ci.org/EUDAT-B2STAGE/http-api.svg)](https://travis-ci.org/EUDAT-B2STAGE/http-api)

NOTE: the B2STAGE HTTP-API is an interface towards other EUDAT services which are subject to modifications and new developments, therefore the functionalities and the implementation will have to be changed accordingly. 


--

## Objectives
This project aims at developing a B2STAGE HTTP-API fot the EUDAT CDI.
The primary goal is to allow users to ingest and retrieve data via a standard RESTful HTTP interface in order to:

- hide the underlying technology from users,
- lower the entry barrier to using EUDAT services,
- simplify integration into existing workflows,
- allow direct access to data assets held with the EUDAT CDI.

The first development is focused on the interaction with B2SAFE, allowing users to transfer and manage data on the "registered" domain.
Over the EUDAT2020 project other functionalities will be added: the development road map is available on the [EUDAT Wiki](https://confluence.csc.fi/display/EUDAT2/Service+building+roadmap)



## Implementation
The API is implemented in Python 3 using the Flask framework (Flask can be used with most web-servers via the WSGI-standard).
To facilitate and speed the development Docker will be used to automate the deployment of the software stack needed.
The API interconnects with EUDAT services' native APIs or libraries.
For B2SAFE (which is built on an iRODS as back end) the interface is implemented using the [python-irodsclient](https://github.com/irods/python-irodsclient).
This project is based on the [HTTP-API base](https://github.com/EUDAT-B2STAGE/http-api-base)



## Documentation

- [User](docs/user/user.md)
- [Developer](docs/development/development.md)
- [Deploy](docs/deploy/deploy.md)




<!--
## Documentation

To be re-written.
-->

<!--

For a more detailed explanation and some deep understanding:

** WARNING: the following pages are not yet updated **

* [Preparing the environment](docs/preparation.md)
* [Running the services](docs/running.md)
* [Developing](docs/client.md)
* [Admin operations](docs/admin.md)

-->

<!--
## Versions

```
$ ./do irods_shell

irods@rodserver:~$ apt-cache showpkg irods-icat | grep -i versions -A 1
Versions:
4.1.8 (/var/lib/dpkg/status)
```
-->

<!--
## quick notes

b2access basic endpoints:
https://eudat.eu/services/userdoc/b2access-service-integration#B2ACCESS_Services_Endpoints

https://eudat-aai.fz-juelich.de:8445/oauth-demo/get_token.jsp
-->
