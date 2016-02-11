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

# Check if init has been executed
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

################################
# EXECUTE OPTIONS

# Init your stack
if [ "$1" == "init" ]; then
    echo "Updating docker images to latest release"
    $initcom pull
    echo "WARNING: Removing old containers/volumes if any"
    echo "(Sleeping some seconds to let you stop in case you made a mistake)"
    sleep 7
    $initcom stop
    $initcom rm -f
    docker volume rm irodsconf
    echo "READY TO INIT"
    $initcom up icat

# Freeze containers
elif [ "$1" == "stop" ]; then
    echo "Freezing the stack"
    $initcom stop

# Remove all containers
elif [ "$1" == "remove" ]; then
    echo "REMOVE CONTAINERS"
    $initcom stop
    $initcom rm -f

# Destroy everything: containers and data saved so far
elif [ "$1" == "clean" ]; then
    echo "REMOVE DATA"
    echo "are you really sure?"
    sleep 5
    $initcom stop
    $initcom rm -f
    for volume in $volumes;
    do
        echo "Remove $volume volume"
        $vcom rm $volume
        sleep 1
    done

# Normal boot
else
    echo "(re)Boot Docker stack"
    $initcom stop
    $initcom rm -f
    docker-compose up -d iclient
    echo "Stack is up:"
    docker-compose ps
    echo "If you need to access the python client container, please run:"
    echo "$ docker exec -it eudatapi_iclient_1 bash"
fi
