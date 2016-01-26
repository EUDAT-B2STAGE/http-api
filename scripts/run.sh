#!/bin/bash

# Confs
initcom="docker-compose -f docker-compose.yml -f init.yml"
volumes="irodsconf irodshome irodsresc eudathome irodsrestlitedb sqldata"

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
vcom="docker volume"
out=`$vcom ls | grep eudathome`
if [ "$out" == "" ]; then
    if [ "$1" != "init" ]; then
        echo "Please init this project."
        echo "You may do so by running:"
        echo "\$ $0 init"
        exit 1
    fi
fi

# Launch data
if [ "$1" == "init" ]; then
    echo "INIT"
    $initcom up icat
elif [ "$1" == "stop" ]; then
    echo "Freezing the stack"
    $initcom stop
elif [ "$1" == "remove" ]; then
    echo "REMOVE CONTAINERS"
    $initcom stop
    $initcom rm -f
elif [ "$1" == "clean" ]; then
    echo "REMOVE DATA"
    echo "are you really sure?"
    #sleep 5
    for volume in $volumes;
    do
        echo "Remove $volume volume"
        $vcom rm $volume
        sleep 1
    done
else
    echo "(re)Boot Docker stack"
    $initcom stop
    $initcom rm -f
    docker-compose up -d iclient
fi