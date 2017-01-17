#!/bin/bash

user="1000"
echo "Fix db permissions"
chown -R $user /dbs /uploads

# echo "Link shared lib"
# mypath="/var/lib/irods/plugins/auth"
# ln -s /sharedlibs$mypath/libgsi.so $mypath

# Create the secret to enable security on JWT tokens (in production)
head -c 24 /dev/urandom > /jwt_tokens/secret.key

echo "Completed"
