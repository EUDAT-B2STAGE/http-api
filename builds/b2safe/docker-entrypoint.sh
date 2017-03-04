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
until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER $IRODS_DB -c "\d" 2> /dev/null;
do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done


# Is it init time?
# (how to know?)

    # YES: do init
        # set user(s)
            # adduser --disabled-password --gecos '' r
            # adduser r sudo
        # install irods + GSI
        # check irods with icommands
        # more users and certificates
        # extra (like b2safe)

    # NO: launch irods

## END

echo sleep
sleep infinity
exit 0

#############################
# Install irods&friends     #
#############################

MYDATA="/tmp/answers"
/prepare_answers $MYDATA
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

# # Fix permissions
# paths="/home/$IRODS_USER /etc/irods /var/lib/irods /etc/grid-security"
# sudo chown -R $UID:$GROUPS $paths
# # Check if it works
# sleep 2
# echo "Testing installation"
# yes $IRODS_PASSWORD | ils 2> /dev/null
# if [ "$?" -ne 0 ]; then
#     echo "Failed to use irods commands!"
#     echo "Please check your internet connection,"
#     echo "as irods configuration need to be validated online..."
#     exit 1
# else
#     # Certifications
#     /init_certificates
#     # B2SAFE extra if any
# 	if [ -f $EXTRA_INSTALLATION_SCRIPT ]; then
# 		echo "Executing: extra configuration"
# 		$EXTRA_INSTALLATION_SCRIPT
#     else
#         echo "No extra installation script"
# 	fi
# fi

# # ################################
# # # Cleanup
# # echo "All done. Cleaning..."
# # sudo rm -rf /tmp/*
