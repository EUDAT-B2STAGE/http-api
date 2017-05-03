#!/bin/bash
set -e

if [ "$1" != 'proxy' ]; then
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

# IF INIT is necessary
if [ "$DOMAIN" != "" ]; then
    echo "Production mode"

    if [ ! -f "$CERTCHAIN" ]; then
        echo "First time access"
        selfsign
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
echo "launching server"
nginx -g 'daemon off;'
exit 0
