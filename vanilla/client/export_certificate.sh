
#############################################
# Become guest (normal certificates)

export IRODS_USER_NAME=guest
export IRODS_HOST=rodserver
export IRODS_PORT=1247
export IRODS_AUTHENTICATION_SCHEME=gsi
export IRODS_ZONE=tempZone
export IRODS_HOME=/tempZone/home/guest

export X509_USER_CERT=/opt/certificates/guest/usercert.pem
export X509_USER_KEY=/opt/certificates/guest/userkey.pem
export X509_CERT_DIR=/opt/certificates/caauth

exit

#############################################
# Install proxy and CA for b2access dev

# copy certificates
cadir="/opt/certificates/caauth"
certdir="certs"
irods_container="eudatapi_icat_1"
docker cp $certdir/b2access.ca.pem $irods_container:$cadir
docker cp $certdir/b2access.ca.signing_policy $irods_container:$cadir
docker cp $certdir/test.pem $irods_container:/tmp

# root inside icat for b2access caauth
docker exec -it --user root $irods_container bash
cd /opt/certificates/caauth
caid=$(openssl x509 -in b2access.ca.pem -hash -noout)
echo $caid
cp b2access.ca.pem ${caid}.0
cp b2access.ca.signing_policy ${caid}.signing_policy
chown -R irods:irods /opt/certificates /tmp/*
cp /opt/certificates/caauth/$caid* /etc/grid-security/certificates/
exit

# irods admin to add new user with proxy
docker exec -it $irods_container bash
export GSI_USER=paolo
mkdir /opt/certificates/$GSI_USER
certout=/opt/certificates/$GSI_USER/test
cp /tmp/test.pem /opt/certificates/$GSI_USER/test
iadmin mkuser $GSI_USER rodsuser
iadmin aua $GSI_USER \
    "$(openssl x509 -in $certout -noout -subject | sed 's/subject= //')"
iadmin lua
exit

# Become paolo inside rest api
docker exec -it eudatapi_rest_1 bash
export IRODS_USER_NAME=paolo
export IRODS_HOST=rodserver
export IRODS_PORT=1247
export IRODS_AUTHENTICATION_SCHEME=gsi
export IRODS_ZONE=tempZone
export IRODS_HOME=/tempZone/home/paolo
export X509_CERT_DIR=/opt/certificates/caauth
export X509_USER_PROXY=/opt/certificates/paolo/test
ils
