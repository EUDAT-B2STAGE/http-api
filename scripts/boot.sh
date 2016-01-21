#!/bin/bash

#############################
# Defaults
apiconf="vanilla/specs/api_init.json"
jsconf="vanilla/specs/js_init.json"

#############################
# Other variables
com="docker-compose"
#services="backend frontend"
services="custombe customfe"
webbuild="bower"

#############################
cd containers

bcom="$com run $webbuild bower install"

# First time install
if [ "$1" == "init" ]; then

    echo "Download docker images"
    docker-compose pull
    echo "Download submodules"
    git submodule init
    git submodule update
    echo "Build bower packages"
    $bcom
    echo "Completed"

# Update repos, packages and images
elif [ "$1" == "update" ]; then

# TO FIX: add custom compose here too

    docker-compose pull
    current=`pwd`
    cd ..
    for service in $services;
    do
        echo "Repo '$service' fetch"
        cd $service
        git pull
        cd ..
    done
    git submodule sync
    git submodule update
    cd $current
    $bcom

# Bower install
elif [ "$1" == "bower" ]; then

    if [ "$2" != "" ]; then
        bcom="${bcom} $2 --save"
        echo "Install package(s): $2"
    fi
    $bcom

# Launch services
else

    if [ -z "$1" ]; then
        echo "Please specify one configuration to use."
        echo "Available configurations:"
        for i in `ls custom`;
        do
            name=`echo $i | sed "s/\.yml//"`
            echo -e "\t$name"
        done
        exit
    fi

    #############################
    # Check compose stack existence
    file="custom/${1}.yml"
    if [ ! -f "$file" ]; then
        echo "File '$file' not found"
        exit 1
    fi
    files="-f docker-compose.yml -f $file"

    #############################
    # CONF check
    echo "# ############################################ #"
    echo "DO NOT FORGET: to change configuration remove:"
    echo -e "\t$apiconf"
    echo -e "\t$jsconf"
    echo "# ############################################ #"
    echo ""

    # Backend
    apidefault="{ \"$1\": \"$1.ini\" }"
    if [ ! -f "../$apiconf" ]; then
        echo "$apidefault" > ../$apiconf
        echo "Written a new '$apiconf' file"
    fi

    # Frontend
    jsdefault="{ \"blueprint\": \"$1\" }"
    if [ ! -f "../$jsconf" ]; then
        echo "$jsdefault" > ../$jsconf
        echo "Written a new '$jsconf' file"
    fi

    #############################
    # Run services if not adding another command
    if [ -z "$2" ]; then
        echo "ACTION: Reboot"
        echo "Cleaning project containers (if any)"
        $com $files stop $services
        $com $files rm -f $services
        echo "Starting up"
        $com $files up -d $services
    else
        if [ "$2" == "start" ]; then
            echo "ACTION: Start"
            $com $files up -d $services
        fi
        if [ "$2" == "stop" ]; then
            echo "ACTION: Stop"
            echo "Freezing services"
            $com $files stop $services
        fi
        if [ "$2" == "remove" ]; then
            echo "ACTION: Removal"
            echo "Destroying services"
            $com $files rm -f $services
        fi
    fi
    # Check up
    if [ "$?" == "0" ]; then
        echo "[$1] configuration. Status:"
        $com $files ps
        # docker volume ls
    fi
fi
