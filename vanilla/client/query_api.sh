#!/bin/bash

######################################
# NOTE: you need to source this script
# e.g.
# $ . query_api.sh help
######################################

if [ "$1" == "help" ]; then
    echo "Usage: . query_api.sh [METHOD]"
    echo ""
    echo "available methods: get, post, put, delete, clean"
    return
fi

IHOME="/tempZone/home/guest"
MIN_INVALID_STATUS="299"
ALL_COMMAND=""

######################################
if [ "$AUTH" == '' ]; then
    echo "Generating authentication token"
    . /tmp/gettoken 2>&1 1> /dev/null
fi

alive=$(http GET $SERVER/api/status 2>&1 1> /dev/null)
if [ "$?" != "0" ]; then
    echo "API status: DOWN!"
    return
fi

echo "Token available as \$TOKEN"
echo ""

if [ "$SERVER" == '' ]; then
    echo "Error with getting server name"
    echo ""
    return
fi

ENDPOINT="$SERVER/api/resources"

######################################
function api_call()
# based on http://www.linuxjournal.com/content/return-values-bash-functions
{
    ##########
    # input
    local  __resultvar=$1

    ##########
    # local  myresult='some value'
    com=""
    if [ "$2" == 'POST' ]; then
        com="http $2 $ENDPOINT?path=${3} $4"
    else
        com="http $2 $ENDPOINT${3} $4"
    fi
    echo "Command: [ $com \"\$AUTH\" ]"
    out=`$com "$AUTH"`
    status=`echo $out | jq '.Meta.status'`
    errors=`echo $out | jq '.Response.errors'`
    if [ "$status" -gt "$MIN_INVALID_STATUS" ]; then
        echo ""
        echo "API called exit with error [$status]:"
        echo $errors | jq
    else
        data=`echo $out | jq '.Response.data'`
        echo $data | jq
    fi

    ##########
    # output
    eval $__resultvar="'$status'"
}

######################################
# POST

if [ "$1" == 'post' -o "$1" == "$ALL_COMMAND" ]; then
    echo "Create directory [POST]"

    api_call result POST "$IHOME/test" "force=True"
    # http://stackoverflow.com/a/9640736/2114395
    if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
fi

######################################
# PUT

if [ "$1" == 'put' -o "$1" == "$ALL_COMMAND" ]; then
    echo "Upload file [PUT]"

    api_call result '--form PUT' "$IHOME/test" "file@/tmp/gettoken force=True"
    if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
fi

######################################
# GET

if [ "$1" == 'get' -o "$1" == "$ALL_COMMAND" ]; then

    # # check empty for error
    # echo "[GET] No parameter"
    # api_call result 'GET'

    echo "[GET] directory listing"
    api_call result GET "$IHOME"
    if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
fi

######################################
# DELETE

if [ "$1" == 'delete' -o "$1" == "$ALL_COMMAND" ]; then

    echo "Remove non empty directory [DELETE]"
    api_call result DELETE "$IHOME/test"

    echo "Remove file [DELETE]"
    api_call result DELETE "$IHOME/test/gettoken"
    if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi

    echo "Remove directory [DELETE]"
    api_call result DELETE "$IHOME/test"
    if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
fi

######################################
# CLEAN

if [ "$1" == 'clean' ]; then
    api_call status DELETE ?debugclean=true
fi

######################################
# THE END
echo ""
