#!/bin/bash

#############################
com="docker-compose"
services="backend frontend"
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

    docker-compose pull
    current=`pwd`
    cd ..
    for service in $services;
    do
        echo "Repo '$service' fetch"
        cd $service
        git pull origin master
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
    #############################
    echo "Cleaning project containers (if any)"
    $com stop $services
    $com rm -f $services
    echo "Starting up"
    $com up -d $services
    if [ "$?" == "0" ]; then
        echo "Up and running:"
        $com ps
        # docker volume ls
    fi
fi
