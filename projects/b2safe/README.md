
# B2SAFE dockerized

This is an effort to maintain an updated iRODS image working,
with B2SAFE extensions installed at the latest version.

## Prototype

Currently the prototype is based on the HTTP-API development branch.

The first draft is composed of three containers: 

1. a simple iRODS `iCAT` server `v4.2.1` with Globus/GSI installed
2. Postgresql for the iCAT database
3. A client to check connecting to iRODS from another container at the very least

## Quick start

```bash
##################
# Clone the latest branch
git clone https://github.com/EUDAT-B2STAGE/http-api.git 
cd http-api
git checkout 0.6.2

##################
# Install the rapydo controller
sudo -H data/scripts/prerequisites.sh
# Initialise the working copy
rapydo init

##################
# Launch containers

## NOTE: if this is the first time 
## it would take some minutes to build images
rapydo --project b2safe start
# check
rapydo --project b2safe status
# verify the irods port working
telnet localhost 1247
## NOTE: you should be able to connect from outside too
## if you have no firewall blocking incoming connections on that port

##################
# Use it!

# Check from another client
rapydo --project b2safe shell iclient
## NOTE: this opens a shell inside a container
# Become the irods administrator
berods
# Use the icommands
ils
iadmin lu

##################
# Destroy containers and data
rapydo --project b2safe clean --rm
```