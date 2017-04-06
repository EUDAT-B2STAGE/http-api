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

echo "hello"


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
sleep infinity
# whoami
exit 0
