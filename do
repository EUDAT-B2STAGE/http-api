#!/bin/bash

# core_branch="master"
# TO BE FIXED when completing the branch
core_branch="last_refactor"

echo "# ############################################ #"
echo -e "\t\tEUDAT HTTP API development"
echo "# ############################################ #"
echo ""

if [ "$1" == "help" -o -z "$1" ]; then
    echo "Available commands:"
    # echo ""
    # echo -e "init:\t\tStartup your repository code, containers and volumes"
    echo ""
    echo -e "check:\tCheck the stack status"
    echo -e "stop:\tFreeze your containers stack"
    echo -e "remove:\tRemove all containers"
    echo -e "clean:\tRemove containers and volumes (BE CAREFUL!)"
    echo ""
    echo -e "irestart:\tRestart the main iRODS iCAT service instance"
    echo -e "addiuser:\tAdd a new certificated user to irods"
    echo -e "irods_shell:\tOpen a shell inside the iRODS iCAT server container"
    echo ""
    echo -e "client_shell:\tOpen a shell to test API endpoints"
    echo -e "server_shell:\tOpen a shell inside the Flask server container"
    echo -e "httpapi_restart:\tRelaunch only the HTTP Flask server "
    echo -e "api_test:\tRun tests with nose (+ coverage)"
    echo ""
    echo -e "push:\tPush code to github"
    echo -e "update:\tPull updated code and images"
    echo ""
    echo -e "***Modes***:"
    echo -e "DEBUG:\tREST API server should be launched using container shell"
    echo -e "DEVELOPMENT:\tREST API server with Flask WSGI and Debug"
    echo -e "PRODUCTION:\tREST API server with Gunicorn behind nginx proxy"
    echo ""
    echo -e "[Mode:DEBUG|DEVELOPMENT|PRODUCTION] [restart|sqladmin|swagger]:\tLaunch the Docker stack using one of the modes available"
    echo -e "logs:\tAttach to all container logs"
    exit 0
fi

#####################
# Confs
subdir="backend"
submodule_tracking="submodules.current.commit"
irodscontainer="icat"
restcontainer="rest"
proxycontainer="proxy"
clientcontainer="client"
vcom="docker volume"
ncom="docker network"

source .env
# cprefix=`basename $(pwd) | tr -d '-'`
cprefix=$COMPOSE_PROJECT_NAME

compose_base="docker-compose -f docker-compose.yml"
compose_all="$compose_base -f composers/debug.yml -f composers/development.yml -f composers/production.yml "
# compose_all="$compose_base -f composers/init.yml -f composers/debug.yml -f composers/development.yml -f composers/production.yml "

# # Init mode
# if [ "$1" == "init" ]; then
#     compose_run="$compose_base -f composers/init.yml"

# Production mode
if [ "$1" == "PRODUCTION" ]; then

    # # Check for REAL certificates
    # if [ ! -f "./certs/nginx.key" -o ! -f "./certs/nginx.crt" ];
    # then

        # # REAL CERTIFICATES
        # echo "Warning: no real certificates..."
        # echo ""
        # echo "To create them you may use the free Letsencrypt service:"
        # echo "https://letsencrypt.org/"
        # echo ""
        # # exit 1
        # sleep 2

        if [ ! -f "./certs/nginx-selfsigned.key" -o ! -f "./certs/nginx-selfsigned.crt" ];
        then
            # SELF SIGNED CERTIFICATES
            echo "Missing certificates."

            echo "To generate self_signed files right now:"
            echo "./confs/create_self_signed_ssl.sh"
            exit 1
        fi

    # fi

    compose_run="$compose_base -f composers/production.yml"

# Development mode
elif [ "$1" == "DEVELOPMENT" ]; then
    compose_run="$compose_base -f composers/development.yml"

# Normal / debug mode
else
    compose_run="$compose_base -f composers/debug.yml"

fi

#####################
warnings=$($compose_run config -q 2>&1)
if [ "$warnings" != "" ]; then
    echo "Failed to validate compose files:"
    echo $warnings
    exit 1
fi

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

    dcheck=`$com ps 2>&1 | grep -i "cannot connect"`
    if [ "$dcheck" != "" ]; then
        echo "Please check if your Docker daemon is running"
        exit 1
    fi
done

if [ "$(ls -A $subdir)" ]; then
    echo "Submodule already exists" > /dev/null
else
    echo "Inizialitazion for the http-api-base submodule"
    git clone https://github.com/EUDAT-B2STAGE/http-api-base.git $subdir
    cd $subdir
    # Go into the current branch
    git checkout $core_branch
    # print latest commit
    echo "Check latest commit"
    git log -n 1
    cd ..
fi

# Update the remote github repos
if [ "$1" == "push" ]; then

    check_container=`$compose_run ps rest | grep -i exit`
    if [ "$check_container" != "" ]; then
        echo "Please make sure that Flask container server is running"
        echo "You may try with the command:"
        echo "$0 DEBUG"
        echo ""
        exit 1
    fi

    if [ "$2" != "force" ]; then
        echo "TO BE FIXED..."
        exit 1
        # testlogs="/tmp/tests.log"
        # echo "Running tests before pushing..."
        # $make_tests > $testlogs
        # if [ "$?" == "0" ]; then
        #     echo "Test are fine!"
        # else
        #     echo "Failed, to test... (see $testlogs file)"
        #     echo "Fix errors before pushing, or run again with:"
        #     echo "$0 $1 force"
        #     exit 1
        # fi
    fi

    echo "Pushing submodule"
    cd $subdir
    git push
    cd ..

    # Save a snapshot of current submodule
    echo "Save submodule status"
    echo -e \
        $(cd $subdir && git log -n 1 --oneline --no-color)"\n"$(cd $subdir && git branch --no-color) \
        > $submodule_tracking

    echo "Pushing main repo"
    git add $submodule_tracking
    git commit
    git push
    echo "Completed"
    exit 0
fi

# Update your code
if [ "$1" == "update" ]; then
    echo "Pulling main repo"
    git pull
    echo "Pulling submodule"
    cd $subdir
    git pull
    cd ..
    # Note: images must be updated after pulling the code
    # otherwise we won't know if new images are requested
    echo "Updating (all) docker images to latest release"
    $compose_all pull
    echo "Done"
    exit 0
fi

networks=`$ncom ls | awk '{print $2}' | grep "^$cprefix"`
volumes=`$vcom ls | awk '{print $NF}' | grep "^$cprefix"`

# Verify the status
if [ "$1" == "check" ]; then
    echo "Stack status:"
    $compose_run ps
    exit 0

# Freeze containers
elif [ "$1" == "stop" ]; then
    echo "Freezing the stack"
    $compose_run stop
    exit 0

# Remove all containers
elif [ "$1" == "remove" ]; then
    echo "REMOVE CONTAINERS"
    $compose_run stop
    $compose_run rm -f
    exit 0

# Destroy everything: containers and data saved so far
elif [ "$1" == "clean" ]; then
    echo "REMOVE DATA"
    echo "are you really sure?"
    sleep 5

    echo "Removing containers"
    $compose_run stop
    $compose_run rm -f
    echo
    sleep 1

    echo "Removing networks"
    for network in $networks;
    do
        # echo "Removing $network"
        $ncom rm $network
    done
    sleep 1

    echo "Removing volumes"
    for volume in $volumes;
    do
        # echo "Removing $volume"
        $vcom rm $volume
    done
    exit 0

elif [ "$1" == "addiuser" ]; then
    echo "Adding a new certificated iRODS user:"
    $compose_run exec $irodscontainer /addusercert $2
    exit 0

elif [ "$1" == "irestart" ]; then
    $compose_run exec $irodscontainer service irods restart
    exit 0

elif [ "$1" == "irods_shell" ]; then
    $compose_run exec $irodscontainer --user irods bash
    exit 0

elif [ "$1" == "server_shell" ]; then
    $compose_run exec $restcontainer bash
    exit 0

elif [ "$1" == "httpapi_restart" ]; then
    $compose_run restart $restcontainer
    exit 0

elif [ "$1" == "api_test" ]; then
    echo "Opening a shell for nose2 tests"
    $compose_run exec rest /bin/bash -c "testwithcoverage"
    exit $?

elif [ "$1" == "client_shell" ]; then
    echo "Opening a client shell"
    $compose_run run --rm --no-deps $clientcontainer bash
    exit 0

# Handle the right logs
elif [ "$1" == "logs" ]; then
    $compose_run logs -f -t --tail="10"
    exit 0

# SSL certificates in production with letsencrypt
elif [ "$1" == "letsencrypt" ]; then
    echo "Creating new letsencrypt certificates"
    $compose_run exec proxy /updatecertificates
    exit 0

elif [ "$1" == "buildall" ]; then
    $compose_run build --pull
    exit 0

elif [ "$1" == "buildone" ]; then
    $compose_run build $2
    exit 0
fi

# Boot up
if [ "$1" == "DEBUG" -o "$1" == "DEVELOPMENT" -o "$1" == "PRODUCTION" ];
then

    echo "Docker stack: booting"

    if [ "$2" == "sql_admin" ]; then
        echo "Administration for relational databases"
        $compose_run up sqladmin
        exit 0
    elif [ "$2" == "swagger" ]; then
        if [ "$1" != "DEBUG" ]; then
            echo "Swagger should run only in debug mode"
            exit 1
        fi
        echo "Note: with your browser"
        swagger_url="http://localhost/swagger-ui/"
        local_url="http://localhost:8080/api/specs"
        echo "open \"$swagger_url?url=$local_url\""
        echo ""
        $compose_run up swagclient
        exit 0
    fi
    elif [ "$2" == "restart" ]; then
        echo "Clean previous containers"
        $compose_run stop
        $compose_run rm -f
    fi

    $compose_run up -d $restcontainer
    status="$?"

    echo "Stack processes:"
    $compose_run ps

    if [ "$status" == "0" ]; then
        $compose_run exec $restcontainer update-ca-certificates
        echo ""
        echo "To access the flask api container:"
        echo "$0 server_shell"
        echo ""
        echo "To query the api server (if running) use the client container:"
        echo "$0 client_shell"

        path="/api/status"

        if [ "$1" == "PRODUCTION" ]; then
            echo "/ # http --follow --verify /tmp/cert.crt awesome.docker$path"
        elif [ "$1" == "DEVELOPMENT" ]; then
            echo "/ # http GET http://apiserver$path"
        else
            echo "/ # http GET apiserver:5000$path"
        fi
        echo ""
    fi

    echo "Boot completed"
    exit 0

fi

echo "Unknown operation '$1'!"
echo "Use \"$0 help\" to see available commands "
exit 1
