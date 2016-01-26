#!/bin/bash

# Check prerequisites
coms="docker docker-compose"
for com in $coms;
do
    dcheck=`which $com`
    if [ "$dcheck" == "" ]; then
        echo "Please install $com to use this project"
        exit 1
    fi
done

# Check init
com="docker volume"
out=`$com ls | grep eudathome`
if [ "$out" == "" ]; then
    echo "Please init this project."
    echo "You may do so by running:"
    echo "\$ $0 init"
    exit 1
fi

initcom="docker-compose -f docker-compose.yml -f init.yml"

# Launch data
if [ "$1" == "init" ]; then
    echo "INIT"
    $initcom up icat
elif [ "$1" == "remove" ]; then
    echo "REMOVE CONTAINERS"
    $initcom stop
    $initcom rm -f
elif [ "$1" == "clean" ]; then
    echo "REMOVE DATA"
    echo "are you really sure?"
    sleep 5
    volumes="irodsconf irodshome irodsresc eudathome irodsrestlitedb"
    for volume in $volumes;
    do
        echo "Remove $volume volume"
        $com rm $volume
        sleep 1
    done
else
    echo "Boot Docker stack"
    docker-compose up -d iclient
fi