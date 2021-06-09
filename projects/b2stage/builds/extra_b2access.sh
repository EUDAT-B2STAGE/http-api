#!/bin/bash

## Add and validate the B2ACCESS certification authority

if [ ! -z "$B2ACCESS_CAS" ]; then
    cd $CADIR
    gridcerts="$GRIDCERTDIR/certificates"

    ## DEV
    label="b2access.ca.dev"
    caid=$(openssl x509 -in $B2ACCESS_CAS/$label.pem -hash -noout)
    # caid=$(openssl x509 -in $label.pem -hash -noout)
    if [ `ls -1 $gridcerts/$caid.* 2> /dev/null | wc -l` != "2" ]; then
        echo "B2ACCESS CA [dev]: label is $caid"
        cp $B2ACCESS_CAS/$label.* $CADIR/
        mv $label.pem ${caid}.0
        mv $label.signing_policy ${caid}.signing_policy
        cp $CADIR/$caid* $gridcerts/
    fi

    ## STAGING
    label="b2access.ca.staging"
    caid=$(openssl x509 -in $B2ACCESS_CAS/$label.pem -hash -noout)
    # caid=$(openssl x509 -in $label.pem -hash -noout)
    if [ `ls -1 $gridcerts/$caid.* 2> /dev/null | wc -l` != "2" ]; then
        echo "B2ACCESS CA [staging]: label is $caid"
        cp $B2ACCESS_CAS/$label.* $CADIR/
        mv $label.pem ${caid}.0
        mv $label.signing_policy ${caid}.signing_policy
        cp $CADIR/$caid* $gridcerts/
    fi

    ## PROD
    label="b2access.ca.prod"
    caid=$(openssl x509 -in $B2ACCESS_CAS/$label.pem -hash -noout)
    if [ `ls -1 $gridcerts/$caid.* 2> /dev/null | wc -l` != "2" ]; then
        echo "B2ACCESS CA [prod]: label is $caid"
        cp $B2ACCESS_CAS/$label.* $CADIR/
        mv $label.pem ${caid}.0
        mv $label.signing_policy ${caid}.signing_policy
        cp $CADIR/$caid* $gridcerts/
    fi

    chown -R $IRODS_USER /opt/certificates
    echo
    echo "Completed B2ACCESS GSI certificates setup"
    echo
fi
