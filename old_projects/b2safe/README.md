
# B2SAFE dockerized

This is an effort to maintain an updated iRODS image working,
with B2SAFE extensions installed at the latest version.

## Prototype

Currently the prototype is based on the HTTP-API development branch.

The first draft is composed of three containers: 

1. a simple iRODS `iCAT` server `v4.2.2` with Globus/GSI installed
2. Postgresql for the iCAT database
3. A client to check connecting to iRODS from another container at the very least

## Quick start

```bash

# NOTE: do not pull from existing repository
# remove any existing repo instead:
rm -rf myb2safe

##################
# Clone the latest development branch
git clone https://github.com/EUDAT-B2STAGE/http-api.git myb2safe
cd myb2safe && git checkout 1.0.2

##################
# Install the rapydo controller
sudo -H data/scripts/prerequisites.sh
# Initialise the working copy
rapydo init

##################
# Launch containers

# Build the normal iRODS iCat image
rapydo --project b2safe --mode simple_irods build

# launch the stack
rapydo --project b2safe start
# check
rapydo --project b2safe status
# verify the irods port working
telnet localhost 1247
## NOTE: you should be able to connect from outside too
## (only if you have no firewall blocking incoming connections on that port)

##################

##################
# Use it!

# Check the current server
rapydo --project b2safe shell icat
## NOTE: this opens a shell inside the main server container
ls /opt/eudat/b2safe
# Become the irods administrator
berods
# Use the icommands
ils
iadmin lu
exit

# Check from another client
rapydo --project b2safe shell iclient
## NOTE: this opens a shell inside a client container
# Become the irods administrator
berods
# Use the same icommands
ils
exit

##################
# Destroy containers and data
rapydo --project b2safe clean --rm
```
