#!/bin/bash

echo "Enabling anonymous user"

# read variables to use the aliases
shopt -s expand_aliases
source ~/.bash_aliases

# create the user
# 'anonymous' is a reserved name
berods -c 'iadmin mkuser anonymous rodsuser'
if [ "$?" != "0" ]; then
    echo "failed to admin users"
    exit 1
fi

# create a home to use
berods -c 'imkdir /$IRODS_ZONE/home/anonymous'
berods -c 'ichmod write anonymous /$IRODS_ZONE/home/anonymous'

# public is readable for anonymous
berods -c 'ichmod read anonymous /$IRODS_ZONE/home/public'
