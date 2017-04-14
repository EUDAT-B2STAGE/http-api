#!/bin/bash
set -e

if [ "$1" != 'rest' ]; then
    echo "Requested custom command:"
    echo "\$ $@"
    $@
    exit 0
fi

######################################
#
# Entrypoint!
#
######################################

# # check environment variables
if [ -z "$VANILLA_PACKAGE" -a -z "$IRODS_HOST" -a -z "ALCHEMY_HOST" ];
then
    echo "Cannot launch API server without base environment variables"
    echo "Please review your '.env' file"
    exit 1
fi

# Defaults
if [ -z APP_MODE ]; then
    APP_MODE="debug"
fi
APIUSERID=$(id -u $APIUSER)

# IF INIT is necessary
secret_file="$JWT_APP_SECRETS/secret.key"
if [ ! -f "$secret_file" ]; then
    echo "First time access"

    # Create the secret to enable security on JWT tokens
    mkdir -p $JWT_APP_SECRETS
    head -c 24 /dev/urandom > $secret_file
    chown -R $APIUSERID $JWT_APP_SECRETS

    # question: should we fix sqllite permissions?
    # answer: we are using postgresql also in development

    echo "Init flask app"
    initialize
    if [ "$?" == "0" ]; then
        echo
    else
        echo "Failed to startup flask!"
        exit 1
    fi

fi

#####################
# Extra scripts
dedir="/docker-entrypoint.d"
for f in `ls $dedir`; do
    case "$f" in
        *.sh)     echo "running $f"; bash "$dedir/$f" ;;
        *)        echo "ignoring $f" ;;
    esac
    echo
done

#####################
# Completed
echo "REST API backend server is ready"

if [ "$app_mode" == 'production' ]; then
    echo "launching uwsgi workers"
    echo "TO DO!"
    exit 1
elif [ "$app_mode" == 'development' ]; then
    echo "launching flask"
    rapydo
else
    echo "Debug mode"
    sleep infinity
fi

exit 0
