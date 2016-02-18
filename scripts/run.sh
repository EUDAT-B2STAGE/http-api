#!/bin/bash

echo "# ############################################ #"
echo -e "\t\tEUDAT HTTP API development"
echo "# ############################################ #"
echo ""

#####################
# Confs
subdir="backend"
restcontainer="rest"
initcom="docker-compose -f docker-compose.yml -f init.yml"
volumes="irodsconf irodshome irodsresc eudathome irodsrestlitedb sqldata"
#####################

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
if [ "$(ls -A backend)" ]; then
    echo "Submodule already exists"
else
    echo "Inizialitazion for the http-api-base submodule"
    git submodule init
    git submodule update
fi

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
    if [ "$?" == "0" ]; then
        echo ""
        echo "Your project is ready to be used."
        echo "Everytime you need to start just run:"
        echo "\$ $0"
    fi

# Update your code
elif [ "$1" == "update" ]; then
    echo "Updating docker images to latest release"
    $initcom pull
    echo "Pulling main repo"
    git pull
    echo "Pulling submodule"
    cd backend
    git pull origin master
    echo "Done"

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
    if [ "$1" != "graceful" ]; then
        echo "Clean previous containers"
        $initcom stop
        $initcom rm -f
    fi
    echo "(re)Boot Docker stack"
    docker-compose up -d $restcontainer
    status="$?"
    echo "Stack status:"
    docker-compose ps
    if [ "$status" == "0" ]; then
        echo "If you need to access the python client container, please run:"
        container_name=`docker ps | grep $restcontainer | awk '{print \$NF}'`
        echo "$ docker exec -it $container_name bash"
    fi
fi
