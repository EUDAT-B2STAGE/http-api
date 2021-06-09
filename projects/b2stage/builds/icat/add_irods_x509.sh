#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 USERNAME"
    exit 1
fi
MYUSER="$1"
mydir="$CERTDIR/$MYUSER"
mkdir -p $mydir

##############################
## CERTIFICATES
##############################

# NOTE TO SELF:
# This must be splitted in two pieces.
# The first one is set the certificates (CA auth + host) -> at init time
# The second one is a binary -> to be called only if necessary

## CA authority
if [ ! -d "$GRIDCERTDIR/certificates" ]; then
    grid-ca-create -noint -dir $CADIR
    yes 1 | grid-default-ca
    # do this if no certificates in simple ca
    cp $GRIDCERTDIR/certificates/* $CADIR
fi
# grid-default-ca -list

if [ ! -s $CADIR/cacert.pem ]; then

    # prefix to copy
    pref=`grid-default-ca -list | grep Loc | sed 's/Location://' | sed 's/0$//' | tr -d ' '`
    cp ${pref}* $CADIR/

    # FIX necessary with GT6
    gt6dir="/var/lib/globus/simple_ca"
    if [ -s "$gt6dir/cacert.pem" ]; then
        echo "Copy globus6 ca cert"
        cp $gt6dir/cacert.pem $CADIR/
    fi
    if [ -s "$gt6dir/grid-ca-ssl.conf" ]; then
        echo "Copy globus6 ca conf"
        cp $gt6dir/grid-ca-ssl.conf $CADIR/
    fi

fi

## HOST
if [ `ls -1 $GRIDCERTDIR/host*.* 2> /dev/null | wc -l` == "3" ]; then
    echo "Host certificate based on gt6"
    # fix permissions for current validated host
    chown -R $IRODS_USER $GRIDCERTDIR/host*
    mkdir -p $CERTDIR/host
    cp $GRIDCERTDIR/host* $CERTDIR/host/
fi

if [ ! -s "$CERTDIR/host/hostcert.pem" ]; then
    echo "no host certificate found"
    yes | grid-cert-request -host $HOSTNAME -force -dir $CERTDIR/host
    yes globus | grid-ca-sign -dir $CADIR \
        -in $CERTDIR/host/hostcert_request.pem -out $CERTDIR/host/hostcert.pem

    mkdir -p /var/lib/irods/.globus
    ln -s /opt/certificates/host/hostkey.pem /var/lib/irods/.globus/
    ln -s /opt/certificates/host/hostcert.pem /var/lib/irods/.globus/
    echo "Created host certificate"
fi

chown -R $IRODS_USER /opt/certificates
echo
echo "Completed basic certificates setup"
echo


##############################
## NEW USER
##############################

# Check
out=`su -c "iadmin lua" $IRODS_USER | grep ^$MYUSER`
if [ "$out" != "" ]; then
    echo "User $MYUSER already exists";
    exit 0
fi

# Create certificate
grid-cert-request -cn $MYUSER -dir $mydir -nopw
if [ "$?" != "0" ]; then
    echo "Failed to create the certificate"; exit 1
fi

# Sign the certificate
certin="$mydir/usercert_request.pem"
certout="$mydir/usercert.pem"
yes globus | grid-ca-sign -dir $CADIR \
    -in $certin -out $certout
# clear

# Check certificate
openssl x509 -in $certout -noout -subject
if [ "$?" == "0" ]; then
    echo "Created signed certificate"
else
    echo "Failed to create the certificate"
    exit 1
fi
chown -R $IRODS_USER $CERTDIR

# Add and configure user to irods
dn=$(openssl x509 -in $certout -noout -subject | sed 's/subject= //')
su -c "iadmin mkuser $MYUSER rodsuser; iadmin aua $MYUSER '$dn'" $IRODS_USER

# Is it admin?
if [ "$2" == "admin" ]; then
    su -c "iadmin moduser $MYUSER type rodsadmin" $IRODS_USER
fi

echo "Added '$MYUSER' to irods GSI authorized user:"
su -c "iadmin lua" $IRODS_USER
