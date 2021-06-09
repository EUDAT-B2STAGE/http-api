#!/bin/bash
set -e


DEVID=$(id -u $IRODS_UNAME)
if [ "$DEVID" != "$CURRENT_UID" ]; then
    echo "Fixing uid of user $IRODS_UNAME from $DEVID to $CURRENT_UID..."
    usermod -u $CURRENT_UID $IRODS_UNAME
fi

GROUPID=$(id -g $IRODS_UNAME)
if [ "$GROUPID" != "$CURRENT_GID" ]; then
    echo "Fixing gid of user $IRODS_UNAME from $GROUPID to $CURRENT_GID..."
    groupmod -og $CURRENT_GID $IRODS_UNAME
fi

# set the current password for 'system' user "irods"
yes $IRODS_PASSWORD | passwd $IRODS_USER

if [ "$1" != 'irods' ]; then
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

# check environment variables
if [ -z "$IRODS_HOST" -o -z "$POSTGRES_HOST" ];
then
    echo "Cannot launch irods without basic environment variables"
    echo "Please review your '.env' file"
    exit 1
fi

# Check postgres at startup
# https://docs.docker.com/compose/startup-order/
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER $IRODS_DB -c "\d" 1> /dev/null 2> /dev/null;
do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Is it init time? If that is the case then this directory is empty:
checkirods=$(ls /etc/irods/)
if [ "$checkirods" == "" ]; then

    #############################
    # Install irods&friends     #
    # install irods 4.2 + GSI
    # it automatically create the irods user
    # it automatically fixes permissions
    # it also checks if server is up at the end
    #############################

    MYDATA="/tmp/answers"
    prepare_answers $MYDATA
    # Launch the installation
    python /var/lib/irods/scripts/setup_irods.py < $MYDATA
    # Verify how it went
    if [ "$?" == "0" ]; then
        rm $MYDATA
        echo ""
        echo "iRODS INSTALLED!"
    else
        echo "Failed to install irods..."
        exit 1
    fi

    # Anonymous user
    if [ "$IRODS_ANONYMOUS" == 1 ]; then
        # enable the anonymous user in irods with the custom script
        ianonymous
    fi

else
    # NO: launch irods
    echo "Already installed. Launching..."

    service irods start
fi

# Extra scripts
# dedir="/docker-entrypoint.d"
# for f in $(ls $dedir); do
#     case "$f" in
#         *.sh)     echo "running $f"; bash "$dedir/$f" ;;
#         *)        echo "ignoring $f" ;;
#     esac
#     echo
# done

# Completed
echo "iRODS is ready"

exec sleep infinity
