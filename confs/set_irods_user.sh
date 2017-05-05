
export IRODS_USER_NAME=guest

export IRODS_USER_NAME=0a646980c779

export IRODS_HOST=rodserver.dockerized.io
export IRODS_PORT=1247
export IRODS_ZONE_NAME=tempZone
export IRODS_AUTHENTICATION_SCHEME=GSI
export IRODS_HOME=/$IRODS_ZONE_NAME/home/$IRODS_USER_NAME

export X509_USER_PROXY=/opt/certificates/$IRODS_USER_NAME/userproxy.crt

export X509_CERT_DIR=/opt/certificates/simple_ca
export X509_USER_CERT=/opt/certificates/$IRODS_USER_NAME/usercert.pem
export X509_USER_KEY=/opt/certificates/$IRODS_USER_NAME/userkey.pem
