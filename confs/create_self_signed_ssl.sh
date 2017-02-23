#!/bin/bash

# Where to store key and cert files
# TO FIX: use this inside the nginx container
key="./certs/nginx-selfsigned.key"
cert="./certs/nginx-selfsigned.crt"

command="openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout $key -out $cert"

# Input values required by the command:
#        Country Name (2 letter code) [AU]:
#        State or Province Name (full name) [Some-State]:
#        Locality Name (eg, city) []:
#        Organization Name (eg, company) [Internet Widgits Pty Ltd]:
#        Organizational Unit Name (eg, section) []:
#        Common Name (e.g. server FQDN or YOUR name) []:
#        Email Address []:


# The most important line is the one that requests the Common Name (e.g. server FQDN or YOUR name).
# You need to enter the domain name associated with your server or, more likely, your server's public IP address.

country='IT'
state='Rome'
locality='Rome'
organization='CINECA'
organization_unit='SCAI'
common_name='awesome.docker'
email='user@nomail.org'

$command 2> /dev/null << EOF
$country
$state
$locality
$organization
$organization_unit
$common_name
$email
EOF

if [ "$?" == "0" ]; then
    echo "Created"
else
    echo "Failed..."
fi

# to read the cert file
# openssl x509 -in /etc/ssl/certs/nginx-selfsigned.crt -text
