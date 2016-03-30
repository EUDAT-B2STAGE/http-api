#!/bin/bash

echo "Fix db permissions"
chown -R 1000 /dbs

# echo "Link shared lib"
# mypath="/var/lib/irods/plugins/auth"
# ln -s /sharedlibs$mypath/libgsi.so $mypath

echo "Completed"
