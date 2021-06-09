#!/bin/bash

# For testing GSI & certificates purposes
add-irods-X509 rodsminer admin

# TODO: check if a different default zone makes some problem here
add-irods-X509 guest

echo
echo "Completed GSI users setup"
echo
# NOTE: now based on Globus toolkit 6

### WARNING: starting from irods 4.2.1 this breaks things
### there is a file /tmp/irodsServer.1247 which seems to be the irods pid...
# echo "Cleaning temporary files"
# rm -rf /tmp/*
