# !/bin/bash
set -e

# DOMAIN="b2stage.cineca.it"
# MODE="--staging"
# MODE=""

# Renewall script
echo "Mode: *$MODE*"
echo "Domain: $DOMAIN"

./acme.sh --issue --debug \
    --fullchain-file ${CERTCHAIN} --key-file ${CERTKEY} \
    -d $DOMAIN -w $WWWDIR $MODE

if [ "$?" == "0" ]; then
    # List what we have
    echo "Completed. Check:"
    ./acme.sh --list

    nginx -s reload
else
    echo "ACME FAILED!"
fi
