#!/bin/bash

user="1000"
echo "Fix db permissions"
chown -R $user /dbs /uploads

# echo "Link shared lib"
# mypath="/var/lib/irods/plugins/auth"
# ln -s /sharedlibs$mypath/libgsi.so $mypath

echo "Completed"
