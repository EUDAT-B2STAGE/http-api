
# notes


## Checks

- irods/b2safe image/stack
- ansible course (better than .env)


## Bugs

- HTTP API to manually trigger the EUDAT replication rule after uploading


## Deploy B2STAGE server

- test upgrade
    + https://github.com/rapydo/issues/issues/71
- verify connection to B2SAFE with rapydo command
    + https://github.com/rapydo/issues/issues/92#issue-299715193
- package for debian
    + https://github.com/rapydo/issues/issues/91


## instructions

0. HTTP API irods user has to be an "irods adminer"
1. install Rancher and add at least one nodes
2. generate API keys for the HTTP API
3. configure Rancher to access the private docker hub/registry
4 add labels to host(s) that will run quality checks
    + host_type=qc

- TODO: clean up once a day with the Janitor in the catalog
    + https://github.com/rancher/community-catalog/tree/master/templates/janitor

<!--
- launch from the catalog an NFS server
    + mount the NFS server folder as a zone in irods server
    + mount the NFS server to every host that will run quality checks 
        in /usr/share/inputs
-->

## done

- auth docs deploy
    + https://github.com/EUDAT-B2STAGE/http-api/issues/99
    + Improved the discussion of what authentication mechanism to enable on your server
- add binary option
    + force it on upload call for seadata
    + open issue for normal b2stage servers
    In [4]: type('test') Out[4]: str
    In [5]: type('test'.encode()) Out[5]: bytes
- fix pretty print
    + test update
    `$ rapydo update --rebuild`
- $ irule "{EUDATCreatePID ...

