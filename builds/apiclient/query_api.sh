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
    echo -e "\t - update PATH FILE"
    echo -e "\t - download PATH"
    echo -e "\t - remove PATH"
    return
fi

######################################
if [ -z "$SERVER" ]; then
    export SERVER="$APP_HOST:$APP_PORT"
fi
alive=$(http GET $SERVER/api/status 2>&1 1> /dev/null)
if [ "$?" != "0" ]; then
    echo "API status: DOWN!"
    return
fi

######################################
IHOME="/tempZone/home/guest"

#####################
# ## HOW TO FORCE TESTING ON OUTSIDE SERVER
# SERVER="https://b2stage.cineca.it"
# IHOME="/tempZone/home/0a646980c779"
# TOKEN="SOMETHING"
# AUTH="Authorization:Bearer $TOKEN"
#####################

MIN_INVALID_STATUS="299"
DEFAULT_INVALID_STATUS="500"
ALL_COMMAND=""

######################################
# Read credentials from current files

dfile="/code/core/rapydo/confs/defaults.yaml"
cfile="/code/custom/specs/eudat.yaml"
jpath="variables.python.backend.credentials"

# Custom
credentials=`yq --json -c ".$jpath" $cfile`
if [ "$credentials" == "null" ]; then
    # if not custom, base
    credentials=`yq --json -c ".$jpath" $dfile`
    if [ "$credentials" == "null" ]; then
        echo "FATAL!"
        echo "No credentials found"
        exit 1
    else
        echo "credentials set"
    fi
fi

username=`echo $credentials | jq .username | tr -d '"'`
password=`echo $credentials | jq .password | tr -d '"'`
export CREDENTIALS="username=$username password=$password"

######################################
if [ "$AUTH" == '' ]; then
    echo "Generating authentication token"
    . /code/gettoken 2>&1 1> /dev/null
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

    # default if not set or number?
    if [ -z "$out" ]; then
        status="$DEFAULT_INVALID_STATUS"
    else
        status=`echo $out | jq '.Meta.status'`
    fi
    # if [ -z "$status" ]; then
    #     ${status:-500}
    # fi

    if [ "$status" -gt "$MIN_INVALID_STATUS" ]; then
        echo ""
        echo "API called exit with error [$status]:"
        errors=`echo $out | jq '.Response.errors'`
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
used="0"


######################################
# POST

if [ "$1" == 'create' -o "$1" == "$ALL_COMMAND" ]; then

    used="1"
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

    used="1"
    path="$IHOME/test"
    if [ ! -z "$2" ]; then
        path="$2"
    fi

    file="/code/gettoken"
    if [ ! -z "$3" ]; then
        file="$3"
    fi

    echo "Upload file [PUT]"

    api_call result '--form PUT' "$path?force=True" "file@$file"
    if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
fi

######################################
# PATCH

if [ "$1" == 'update' -o "$1" == "$ALL_COMMAND" ]; then

    used="1"
    path="$IHOME/test/gettoken"
    if [ ! -z "$2" ]; then
        path="$2"
    fi

    file="myfile"
    if [ ! -z "$3" ]; then
        file="$3"
    fi

    echo "Update file name [PATCH]"

    api_call result PATCH "$path" "newname=$file"
    if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
fi

######################################
# GET

if [ "$1" == 'list' -o "$1" == "$ALL_COMMAND" ]; then

    used="1"
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

    used="1"
    if [ ! -z "$2" ]; then
        path="$2"
        echo "Remove path $path [DELETE]"
        api_call result DELETE "$path"
    else
        echo "Remove non empty directory [DELETE]"
        api_call result DELETE "$IHOME/test"

        echo "Remove file [DELETE]"
        api_call result DELETE "$IHOME/test/myfile"
        if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi

        echo "Remove directory [DELETE]"
        api_call result DELETE "$IHOME/test"
        if [ "$result" -gt "$MIN_INVALID_STATUS" ]; then return; fi
    fi
fi

######################################
# CLEAN

if [ "$1" == 'clean' ]; then
    used="1"
    api_call status DELETE ?debugclean=true
fi

######################################
# THE END
if [ "$used" == "0" ]; then
    echo "Unknown action '$1'. Check available commands with:"
    echo ""
    echo "$ . query_api.sh help"
fi
echo ""
