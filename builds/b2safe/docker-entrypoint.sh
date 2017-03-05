#!/bin/bash

######################################
#
# Entrypoint!
#
######################################

## START
echo start

# check environment variables

# Check postgres at startup
# https://docs.docker.com/compose/startup-order/
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER $IRODS_DB -c "\d" 1> /dev/null 2> /dev/null;
do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done


# Is it init time?
checkirods=$(ls /etc/irods/)
if [ "$checkirods" == "" ]; then

    #############################
    # Install irods&friends     #
    # install irods 4.2 + GSI
    # it automatically create the irods user
    # it automatically fixes permissions
    # it also checks if server is up at the end
    #############################

    MYDATA="/tmp/answers"
    sudo -E /prepare_answers $MYDATA
    # Launch the installation
    sudo python /var/lib/irods/scripts/setup_irods.py < $MYDATA
    # Verify how it went
    if [ "$?" == "0" ]; then
        echo ""
        echo "iRODS INSTALLED!"
    else
        echo "Failed to install irods..."
        exit 1
    fi

    # set guest/rodsminer certificate user(s)

    # extra script

    # Cleanup
    echo "All done. Cleaning..."
    sudo rm -rf /tmp/*

else
    # NO: launch irods
    echo "Already installed. Launching..."
    service irods start

fi
## END

echo "iRODS is ready"
sleep infinity
exit 0

# Certifications
/init_certificates
# B2SAFE extra if any
if [ -f $EXTRA_INSTALLATION_SCRIPT ]; then
	echo "Executing: extra configuration"
	$EXTRA_INSTALLATION_SCRIPT
else
    echo "No extra installation script"
fi

