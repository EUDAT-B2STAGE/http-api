#!/bin/bash
set -e

if [ -z "$2" ]; then
    echo "USAGE:"
    echo "$ $0 user IRODS_USER"
    echo "$ $0 gsi IRODS_GSI_USER"
    echo
    echo "Available users:"
    if [ "$1" == 'gsi' ]; then
        for i in `ls $CERTDIR/*/usercert.pem 2> /dev/null`;
        do
            echo -e "GSI CERT:\t$i"
        done
        for i in `ls $CERTDIR/*/.username 2> /dev/null`;
        do
            user=$(cat $i)
            echo -e "PROXY USER:\t$user -> $i"
        done
    elif [ "$1" == 'user' ]; then
        iadmin lu
    else
        echo "unknown user type '$1'"
    fi
    exit 1
fi

# MYUSER="guest"
# MYUSER="rodsminer"
MYUSER=$2
# export IRODS_HOST=rodserver
# export IRODS_PORT=1247
# export IRODS_ZONE=tempZone

export IRODS_SWITCH=1
export IRODS_HOME=/$IRODS_ZONE/home/$MYUSER

if [ "$1" == 'gsi' ]; then
    export IRODS_USER_NAME=$MYUSER
    export IRODS_AUTHENTICATION_SCHEME=gsi
    export X509_CERT_DIR=$CERTDIR/simple_ca
    export X509_USER_CERT=$CERTDIR/$MYUSER/usercert.pem
    export X509_USER_KEY=$CERTDIR/$MYUSER/userkey.pem
elif [ "$1" == 'user' ]; then
    # https://docs.irods.org/4.1.3/icommands/administrator/#iadmin
    # The admin can also alias as any user
    # via the 'clientUserName' environment variable.
    export clientUserName=$MYUSER
else
    echo "unknown user type '$1'"
    exit 1
fi

echo "Switched to: $MYUSER"
echo "Opening a new shell. Test with: $ ils \$IRODS_HOME/"
echo
bash
