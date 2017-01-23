
export IRODS_HOST=rodserver
export IRODS_PORT=1247
export IRODS_ZONE_NAME=tempZone
export IRODS_AUTHENTICATION_SCHEME=GSI
export IRODS_AUTHSCHEME=GSI
export X509_CERT_DIR=/opt/certificates/caauth

USER=guest
export IRODS_USER_NAME=$USER
export IRODS_HOME=/tempZone/home/$USER
export X509_USER_CERT=/opt/certificates/$USER/usercert.pem
export X509_USER_KEY=/opt/certificates/$USER/userkey.pem
