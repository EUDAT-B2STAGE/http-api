#!/bin/bash

echo "# ############################################ #"
echo -e "\t\tEUDAT HTTP API development"
echo "# ############################################ #"
echo ""

if [ "$1" == "help" -o -z "$1" ]; then
    echo "Available commands:"
    echo ""
    echo -e "init:\t\tStartup your repository code, containers and volumes"
    echo -e "graceful:\tTry to bring up only missing containers"
    echo -e "restart:\t(Re)Launch the Docker stack"
    echo -e "irestart:\tRestart the main iRODS iCAT service instance"
    echo -e "addiuser:\tAdd a new certificated user to irods"
    echo ""
    echo -e "check:\tCheck the stack status"
    echo -e "stop:\tFreeze your containers stack"
    echo -e "remove:\tRemove all containers"
    echo -e "clean:\tRemove containers and volumes (BE CAREFUL!)"
    echo ""
    echo -e "irods_shell:\tOpen a shell inside the iRODS iCAT server container"
    echo -e "server_shell:\tOpen a shell inside the Flask server container"
    echo -e "client_shell:\tOpen a shell to test API endpoints"
    echo -e "api_test:\tRun tests with nose (+ coverage)"
    echo ""
    echo -e "push:\tPush code to github"
    echo -e "update:\tPull updated code and images"
    echo ""
    exit 0
fi

#####################
# Confs
subdir="backend"
submodule_tracking="submodules.current.commit"
irodscontainer="icat"
restcontainer="rest"
clientcontainer="apitests"
compose="docker-compose"
vcom="docker volume"
initcom="$compose -f $compose.yml -f init.yml"
allcompose="$compose -f $compose.yml -f $compose.test.yml -f init.yml"
vprefix="httpapi_"
#####################

# Check prerequisites
coms="docker $compose"
for com in $coms;
do
    dcheck=`which $com`
    if [ "$dcheck" == "" ]; then
        echo "Please install $com to use this project"
        exit 1
    fi
done
if [ "$(ls -A $subdir)" ]; then
    echo "Submodule already exists" > /dev/null
else
    echo "Inizialitazion for the http-api-base submodule"
    git clone https://github.com/EUDAT-B2STAGE/http-api-base.git $subdir
    # git submodule init
    # git submodule update --remote
    cd $subdir
    git checkout master
    cd ..
fi

# Update the remote github repos
if [ "$1" == "push" ]; then

    echo "Pushing submodule"
    cd $subdir
    git push

    # Save a snapshot of current submodule
    echo -e $(git show --pretty=%H)"\n"$(git show-branch --current --no-color) > ../$submodule_tracking

    echo "Pushing main repo"
    cd ..
    git add $submodule_tracking
    git commit
    git push
    echo "Completed"
    exit 0
fi

# Update your code
if [ "$1" == "update" ]; then
    echo "Updating docker images to latest release"
    $allcompose pull
    echo "Pulling main repo"
    git pull
    echo "Pulling submodule"
    cd $subdir
    git pull
    echo "Done"
    exit 0
fi

# Check if init has been executed

volumes=`$vcom ls | awk '{print $NF}' | grep "^$vprefix"`
#echo -e "VOLUMES are\n*$volumes*"
if [ "$volumes"  == "" ]; then
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
    # echo "Updating docker images to latest release"
    # $allcompose pull
    echo "WARNING: Removing old containers/volumes if any"
    echo "(Sleeping some seconds to let you stop in case you made a mistake)"
    sleep 7
    echo "Containers stopping"
    $allcompose stop
    echo "Containers deletion"
    $allcompose rm -f
    if [ "$volumes"  != "" ]; then
        echo "Destroy volumes:"
        docker volume rm $volumes
    fi
    echo "READY TO INIT"
    $initcom up icat rest
    if [ "$?" == "0" ]; then
        echo ""
        echo "Your project is ready to be used."
        echo "Everytime you need to start just run:"
        echo "\$ $0 graceful"
        echo ""
    fi

# Verify the status
elif [ "$1" == "check" ]; then
    echo "Stack status:"
    $allcompose ps

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

elif [ "$1" == "addiuser" ]; then
    container_name=`docker ps | grep $irodscontainer | awk '{print \$NF}'`
    echo "Adding a new certificated iRODS user:"
    docker exec -it $container_name /addusercert $2

elif [ "$1" == "irestart" ]; then
    container_name=`docker ps | grep $irodscontainer | awk '{print \$NF}'`
    docker exec -it $container_name /bin/bash /irestart

elif [ "$1" == "irods_shell" ]; then
    container_name=`docker ps | grep $irodscontainer | awk '{print \$NF}'`
    docker exec -it $container_name bash

elif [ "$1" == "server_shell" ]; then
    container_name=`docker ps | grep $restcontainer | awk '{print \$NF}'`
    docker exec -it $container_name bash

elif [ "$1" == "api_test" ]; then
    echo "Opening a shell for nose2 tests"
    docker-compose exec rest ./tests.sh

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
elif [ "$1" == "graceful" ]; then

    echo "(re)Boot Docker stack"
    docker-compose up -d $restcontainer
    status="$?"
    echo "Stack processes:"
    docker-compose ps
    if [ "$status" == "0" ]; then
        echo ""
        echo "To access the flask api container, please run:"
        echo "$0 server_shell"
    fi

elif [ "$1" == "restart" ]; then

    echo "Clean previous containers"
    $allcompose stop
    $allcompose rm -f

    echo "Boot Docker stack"
    docker-compose up -d $restcontainer
    status="$?"
    echo "Stack processes:"
    docker-compose ps
    if [ "$status" == "0" ]; then
        echo ""
        echo "To access the flask api container, please run:"
        echo "$0 server_shell"
    fi
else
    echo "Unknown operation '$1'!"
    echo "Use \"$0 help\" to see available commands "
    exit 1
fi
