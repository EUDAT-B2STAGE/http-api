
# v0.5.2-beta (*next*)
**due date**: July 15, 2017
**milestone**: [beta version 6](https://github.com/EUDAT-B2STAGE/http-api/milestone/3)

## features
- linking
    - b2access production
    - b2safe production

# v0.5.1-beta (*current*)
**due date**: June 30, 2017
**milestone**: [beta version 5](https://github.com/EUDAT-B2STAGE/http-api/milestone/3)

## features

- performances
- more unittests

# v0.5.0-beta
**due date**: June 15, 2017
**milestone**: [beta version 4](https://github.com/EUDAT-B2STAGE/http-api/milestone/7)

## features

- Cleaner scaffold as a rapydo project (see the [rapydo issue](https://github.com/rapydo/issues/issues/23#issuecomment-307377366))
- B2SAFE metadata [#65]
- Bug fixes

# v0.4.0-beta
**due date**: June 05, 2017
**milestone**: [beta version 3](https://github.com/EUDAT-B2STAGE/http-api/milestone/6)

## features

- shorter token [#57]
- rapydo compliant [#60]
- put operation returning the PID [#61]
- bug fixes [#59]

---

# v0.3.1-beta
**due date**: May 15, 2017
**milestone**: [beta version 2](https://github.com/EUDAT-B2STAGE/http-api/milestone/5?closed=1)

## features

- [#39] automatical refresh of B2ACCESS certificate proxy 
- [#45] pids endpoint 
- [#54] checksum in metadata 
- First regular milestone reached in two weeks

---

# v0.3.0-beta
**due date**: Apr 30, 2017
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
**due date**: Jan 20, 2017
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
**date**: Nov 25, 2016

## features

- Authentication through B2ACCESS credentials
- Basic endpoint for upload, download, remove and listing of data into B2SAFE
- Documentation for [user testing](https://github.com/EUDAT-B2STAGE/http-api/blob/master/docs/user/user.md)

## prototype

First prototype [is online](https://b2stage.cineca.it/api/status):
- based completely on docker
- pointing to [B2ACCESS development server](https://unity.eudat-aai.fz-juelich.de:8443/home/home)
