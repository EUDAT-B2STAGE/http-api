
# Latest updates

to be defined

# Bologna WP5 F2F meeting

---


## Before the meeting

- Connect the test instance (b2stage.cineca.it) to B2SAFE devel instance
- Python script to test the endpoint (with requests)?
- Session on extending the HTTP API base/core repository

---

## Topics for the parallel sessions


### Current state

- **Presentation of the alpha release**
    + demo with prototype online
    + show B2ACCESS authorization
- **Open issues**
    - generic discussion
        + Data domains: clarify registered and workspace data domain.
        + Pluggable backend
        + Data pilot: *Community testing*
    - B2ACCESS
        + B2SAFE users DN not synced with B2ACCESS
        + How to test/mock B2ACCESS?


### Roadmap


- **Towards a production release**
    + documentation for project deploy (both with and w/o Docker)
    + documentation for developers
    + improve responses
    + profile/performances
    + internal API for metadata management
        * local GraphDB (B2STAGE HTTP-API for managing all the metadata store operations)
    + issues
        * which platform to support and how (python and kernel versions)
    + timeline
- **Long term**
    + *internal endpoints* for other EUDAT services (B2SHARE, B2FIND)?
    + timeline


### HTTP specifications document


[//]: # (Comment: Generic or specific for B2STAGE?)

- **Scope**
- **Owner**


---


## After the meeting

- **Redefine ROADMAP and schedule deadlines**


---


# Future topics and issues


To be discussed


[//]: # (- documentation for project deploy)
[//]: # (- unittest)
[//]: # (    + refactor all code that is duplicated [repeated put and post, json dumps])
[//]: # (    + mock test b2access handshake)
[//]: # (    + proxy refresh)
[//]: # (- performances)
[//]: # (    + profile)
[//]: # (    + benchmark)
[//]: # (    + cache)
[//]: # (    + load balancing proxy)
[//]: # (- SSL)
[//]: # (    + automatic creation of certificates from letsencrypt)
[//]: # (    + automatic update every 3 months with cronjob?)
[//]: # (- improve responses)
[//]: # (    + create a standard bearer-token response)
[//]: # (    + also a better standard for all resources responses)
[//]: # (    + add one example of api call with curl inside login output Meta)
[//]: # (- allow configuration files/options)
[//]: # (    + set at docker level across containers)
[//]: # (- Look into `TOFIX` labeled notes inside the code)
[//]: # (- GraphDB neo4j)
[//]: # (    + test bolt native driver)
[//]: # (    + write Eudat models used in B2SAFE metadata parser)
[//]: # (- iRODS related)
[//]: # (    + test python official driver with python3)
[//]: # (    + irods 4.2)
[//]: # (    + add irods 4.2 b2safe rules with python new rule engine)
