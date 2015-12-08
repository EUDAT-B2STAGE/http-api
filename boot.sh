#!/bin/bash

#############################
com="docker-compose"
services="backend frontend"
webbuild="bower"

#############################
cd containers

# Bower install
if [ "$1" == "bower" ]; then


    bcom="$com run $webbuild bower install"
    if [ "$2" != "" ]; then
        bcom="${bcom} $2 --save"
        echo "Install package(s): $2"
    else
        docker-compose pull
        # git submodule init
        git submodule sync
        git submodule update
        echo "Build bower packages"
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
