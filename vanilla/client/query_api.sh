#!/bin/bash

######################################
# NOTE: you need to source this script
# e.g.
# $ . query_api.sh help
######################################

if [ "$1" == "help" ]; then
    echo "Usage: . query_api.sh [METHOD]"
    echo ""
    # echo "available methods: get, post, put, delete, clean"
    echo "available methods:"
    echo ""
    echo -e "\t - list PATH"
    echo -e "\t - create PATH"
    echo -e "\t - upload PATH FILE"
    echo -e "\t - download PATH"
    echo -e "\t - remove PATH"
    return
fi

## // TO FIX:
# add parameters like path for the method or similar?

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

ENDPOINT="$SERVER/api/namespace"

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

    # default if not set or number?
    if [ -z "$status" ]; then
        ${status:-500}
    fi

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

if [ "$1" == 'create' -o "$1" == "$ALL_COMMAND" ]; then

    path="$IHOME/test"
    if [ ! -z "$2" ]; then
        path="$2"
    fi

    echo "Create directory $path [POST]"

    api_call result POST "$path" "force=True"
    # http://stackoverflow.com/a/9640736/2114395
    if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
fi

######################################
# PUT

if [ "$1" == 'upload' -o "$1" == "$ALL_COMMAND" ]; then

    path="$IHOME/test"
    if [ ! -z "$2" ]; then
        path="$2"
    fi

    file="/tmp/gettoken"
    if [ ! -z "$3" ]; then
        file="$3"
    fi

    echo "Upload file [PUT]"

    api_call result '--form PUT' "$path" "file@$file force=True"
    if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
fi

######################################
# GET

if [ "$1" == 'list' -o "$1" == "$ALL_COMMAND" ]; then

    path="$IHOME"
    if [ ! -z "$2" ]; then
        path="$2"
    fi

    echo "[GET] directory listing"
    api_call result GET "$path"
    if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
fi

######################################
# DELETE

if [ "$1" == 'remove' -o "$1" == "$ALL_COMMAND" ]; then

    if [ ! -z "$2" ]; then
        path="$2"
        echo "Remove path $path [DELETE]"
        api_call result DELETE "$path"
    else
        echo "Remove non empty directory [DELETE]"
        api_call result DELETE "$IHOME/test"

        echo "Remove file [DELETE]"
        api_call result DELETE "$IHOME/test/gettoken"
        if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi

        echo "Remove directory [DELETE]"
        api_call result DELETE "$IHOME/test"
        if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
    fi
fi

######################################
# CLEAN

if [ "$1" == 'clean' ]; then
    api_call status DELETE ?debugclean=true
fi

######################################
# THE END
echo ""
