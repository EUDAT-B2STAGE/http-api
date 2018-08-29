
# v1.0.4 (*near future*)

## features

- to be defined

# v1.0.3 (*current*)
**due date**: June 30th, 2018

## features

- better support to SeaData.net project
- bug fixes

# v1.0.2 (*stable*)
**due date**: April 30th, 2018

## features

- improve deploy documentation
- aspects to be defined together with the communities

# v1.0.1
**due date**: January 21th, 2018

## features

- Mostly bug fixes

# v1.0.0 (*first stable release*)
**due date**: October 24th, 2017
**milestone**: [stable release](https://github.com/EUDAT-B2STAGE/http-api/milestones/8)

## features

- Benchmarks #20
- Unittests upgrade (from `nose2` to `py.test`) #105
- A publish endpoint to make data available to anyone/anonymous #72
- PIDS refactor #106
- Automatically recover from failures #103
- Landing page #42
- Bug fixes

## known issues

Currently B2ACCESS and B2SAFE are facing problems in sharing certificated credentials. This is under investigation and will be discussed in the upcoming developer meeting. It is not an issue related to B2STAGE HTTP-API code.

# v0.6.1-rc2
**due date**: September 9th, 2017
**project**: [release candidate 2](https://github.com/EUDAT-B2STAGE/http-api/milestone/9)

## features

- Access directly with B2SAFE credentials #83
- Upgrade an existing installation #87
- B2safe based accounting for all endpoints #88
- Different response when calling `/auth/askauth` not from a browser #92
- Certificates folder name b2access #94
- Python client template #95
- New bugs #96
- Using curl option -u to pass b2safe credentials #97
- Update documentation for authentication via b2safe credentials #98

# v0.6.0-rc1
**due date**: July 31th, 2017
**milestone**: [release candidate 1](https://github.com/EUDAT-B2STAGE/http-api/milestone/3)

## features

- Access directly with B2SAFE credentials #83
- Fix prerequisites installation #84
- Coverage badge #76
- Easier production mode #75
- Data streaming #71
- Get all B2SAFE Metadata #65
- Bugs #59

# v0.5.1-beta
**due date**: July 07th, 2017
**milestone**: [beta version 5](https://github.com/EUDAT-B2STAGE/http-api/milestone/3)

## features

- performances
- more unittests

# v0.5.0-beta
**due date**: June 15th, 2017
**milestone**: [beta version 4](https://github.com/EUDAT-B2STAGE/http-api/milestone/7)

## features

- Cleaner scaffold as a rapydo project (see the [rapydo issue](https://github.com/rapydo/issues/issues/23#issuecomment-307377366))
- B2SAFE metadata #65
- Bug fixes

# v0.4.0-beta
**due date**: June 05th, 2017
**milestone**: [beta version 3](https://github.com/EUDAT-B2STAGE/http-api/milestone/6)

## features

- shorter token #57
- rapydo compliant #60
- put operation returning the PID #61
- bug fixes #59

---

# v0.3.1-beta
**due date**: May 15th, 2017
**milestone**: [beta version 2](https://github.com/EUDAT-B2STAGE/http-api/milestone/5?closed=1)

## features

- #39 automatical refresh of B2ACCESS certificate proxy 
- #45 pids endpoint 
- #54 checksum in metadata 
- First regular milestone reached in two weeks

---

# v0.3.0-beta
**due date**: April 30th, 2017
**milestone**: none

## features
- Contributing to [prc](https://github.com/irods/python-irodsclient) irods driver for python ([python 3 support](https://github.com/irods/python-irodsclient/pull/62) and [gsi integration](https://github.com/irods/python-irodsclient/pull/57))
- Refactor of the core (now called [RAPyDo](https://github.com/rapydo)):
    - docker-compose yaml format v3
         - custom configuration moved into one place
         - switched to docker builds for images
    - services injections as flask extensions
    - services detection with compose v3 variables
- Integration of `prc` as flask extension inside RAPyDo services
- EPIC PID and `B2HANDLE` first integration
- `Letsencrypt` automatization with a dedicated proxy docker build
- Branch dedicated to a community [use case](https://github.com/EUDAT-B2STAGE/http-api/tree/mongo)
- Starting the integration of [gitbook](https://rapydo.gitbooks.io/rapydo/content/) for the documentation
- User (development) testing
- Lots of bug fixes 

---

# v0.2-alpha
**commit**: 643ed4a
**due date**: January 20th, 2017
**milestone**: [Consolidations](https://github.com/EUDAT-B2STAGE/http-api/milestone/4)

## features

- Swagger integration
- Core refactoring to follow what swagger has unlocked
- B2SAFE and B2ACCESS development integration for online prototype
- `http-api-base` merge from concurrent projects
- Participated in adding GSI authentication into irods python official client
- Global better logging
- Various bug fixes

---

# v0.1-alpha
**commit**: 0e8d084
**date**: November 25th, 2016

## features

- Authentication through B2ACCESS credentials
- Basic endpoint for upload, download, remove and listing of data into B2SAFE
- Documentation for [user testing](https://github.com/EUDAT-B2STAGE/http-api/blob/master/docs/user/user.md)

## prototype

First prototype [is online](https://b2stage-test.cineca.it/api/status):
- based completely on docker
- pointing to [B2ACCESS development server](https://unity.eudat-aai.fz-juelich.de:8443/home/home)
