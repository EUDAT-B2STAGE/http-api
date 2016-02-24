#!/bin/bash

echo "# ############################################ #"
echo -e "\t\tEUDAT HTTP API development"
echo "# ############################################ #"
echo ""

#####################
# Confs
subdir="backend"
restcontainer="rest"
clientcontainer="apitests"
compose="docker-compose"
initcom="$compose -f $compose.yml -f init.yml"
allcompose="$compose -f $compose.yml -f $compose.test.yml -f init.yml"
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
    echo "Submodule already exists" > /dev/null
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
    $allcompose pull
    echo "WARNING: Removing old containers/volumes if any"
    echo "(Sleeping some seconds to let you stop in case you made a mistake)"
    sleep 7
    $allcompose stop
    $allcompose rm -f
    docker volume rm irodsconf
    echo "READY TO INIT"
    $initcom up icat
    if [ "$?" == "0" ]; then
        echo ""
        echo "Your project is ready to be used."
        echo "Everytime you need to start just run:"
        echo "\$ $0"
        echo ""
    fi

# Update your code
elif [ "$1" == "update" ]; then
    echo "Updating docker images to latest release"
    $allcompose pull
    echo "Pulling main repo"
    git pull
    echo "Pulling submodule"
    cd backend
    git pull origin master
    echo "Done"

# Freeze containers
elif [ "$1" == "stop" ]; then
    echo "Freezing the stack"
    $allcompose stop

# Remove all containers
elif [ "$1" == "remove" ]; then
    echo "REMOVE CONTAINERS"
    $allcompose stop
    $allcompose rm -f

# Destroy everything: containers and data saved so far
elif [ "$1" == "clean" ]; then
    echo "REMOVE DATA"
    echo "are you really sure?"
    sleep 5
    $allcompose stop
    $allcompose rm -f
    for volume in $volumes;
    do
        echo "Remove $volume volume"
        $vcom rm $volume
        sleep 1
    done

elif [ "$1" == "server_shell" ]; then
    container_name=`docker ps | grep $restcontainer | awk '{print \$NF}'`
    docker exec -it $container_name bash

elif [ "$1" == "client_shell" ]; then
    echo "Opening a client shell"
    echo "You may use the 'httpie' library (http command), e.g.:"
    echo ""
    echo "$ http GET http://api:5000/api/verify"
    echo ""
    compose="docker-compose -f docker-compose.yml -f docker-compose.test.yml"
    $compose up --no-deps -d apitests
    container_name=`docker ps | grep $clientcontainer | awk '{print \$NF}'`
    docker exec -it $container_name sh


# Normal boot
else
    if [ "$1" != "graceful" ]; then
        if [ "$1" != "" ]; then
            echo "Unknown command '$1'!"
            exit 1
        fi

        echo "Clean previous containers"
        $allcompose stop
        $allcompose rm -f
    fi

    echo "(re)Boot Docker stack"
    docker-compose up -d $restcontainer
    status="$?"
    echo "Stack status:"
    docker-compose ps
    if [ "$status" == "0" ]; then
        echo ""
        echo "To access the flask api container, please run:"
        echo "scripts/run.sh server_shell"
    fi
fi
