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

# TO BE COMPLETED!

# # Check irods at startup
# until  psql -h $POSTGRES_HOST -U $POSTGRES_USER $IRODS_DB -c "\d" 1> /dev/null 2> /dev/null;
# do
#   >&2 echo "irods is unavailable - sleeping"
#   sleep 1
# done

# # Is it init time?
# checkirods=$(ls /etc/irods/)
# if [ "$checkirods" == "" ]; then

    # INIT

    # Fix sqllite permissions?

    # # Create the secret to enable security on JWT tokens (in production)
    # mkdir -p /jwt_tokens
    # head -c 24 /dev/urandom > /jwt_tokens/secret.key
    # # chown -R 999 /jwt_tokens

# else

#     echo "Launching"

# fi

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

# Completed
echo "REST API backend server is ready"
sleep 10000d
# sleep infinity
exit 0