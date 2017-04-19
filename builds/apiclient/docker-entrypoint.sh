#!/bin/bash
set -e

if [ "$1" != 'client' ]; then
    # echo "Requested custom command:"
    # echo "\$ $@"
    $@
    exit 0
fi

######################################
#
# Entrypoint!
#
######################################

if [ "$API_PORT" == "" ]; then
    ip=$(host -4 myproxy.dockerized.io | grep 'has address' | awk '{print $NF}')
    # echo "Found ip *$ip*"
    echo "$ip $DOMAIN" >> /etc/hosts
    echo "updated hosts with $DOMAIN"
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

# Completed
echo "Client for HTTP API is ready"
# bash -c "su - $GUEST_USER"
bash -c "su $GUEST_USER"
echo "Client closed"
exit 0
