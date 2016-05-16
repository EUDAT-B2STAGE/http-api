#!/bin/bash

#############################
# Defaults
apiconf="vanilla/specs/api_init.json"
jsconf="vanilla/specs/js_init.json"

#############################
# Other variables
project="restangulask"
compose_com="docker-compose"
webbuild="bower"
volume_prefix="restangulask_${1}_"
fronted_container="customfe"
backend_container="custombe"
submodule_repo="backend"
submodule_git="https://github.com/EUDAT-B2STAGE/http-api-base.git"
services="$backend_container $fronted_container"
submodule_tracking="submodules.current.commit"

#############################
echo "# ############################################ #"
echo -e "\t\tRestangulask"
echo "# ############################################ #"
echo ""

#####################
# Check prerequisites
coms="docker $compose_com"
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

#############################
cd containers

if [ "$1" != "help" ]; then

    if [ -z "$1" ]; then
        echo "Please specify one configuration to use."
        echo "Available configurations:"
        for i in `ls custom`;
        do
            name=`echo $i | sed "s/\.yml//"`
            echo -e "\t$name"
        done
        exit
    elif [ "$1" != "help" ]; then
        echo "### SELECTED BLUEPRINT: [$1]"
        echo ""
    fi

    #############################
    # Check compose stack existence
    file="custom/${1}.yml"
    if [ ! -f "$file" ]; then
        echo "File 'containers/$file' not found!"
        echo "You might start up copying 'demo.yml'."
        exit 1
    fi
    files="-f docker-compose.yml -f $file"

    # Remove previous configuration
    #echo "Clean configuration files"
    if [ -f "../$apiconf" ]; then
        rm ../$apiconf
    fi
    if [ -f "../$jsconf" ]; then
        rm ../$jsconf
    fi
fi

if [ "$1" == "help" -o -z "$2" ]; then
    echo "Usage: $0 BLUEPRINT COMMAND [OPTIONS]"
    echo ""
    echo "Available list of COMMANDs:"
    echo ""
    echo -e "init:\t\tStartup your repository code, containers and volumes"
    echo -e "graceful:\tTry to bring up only missing containers"
    echo -e "restart:\t(Re)Launch the Docker stack"
    echo -e "status:\tCheck the stack status"
    echo -e "stop:\tFreeze your containers stack"
    echo -e "remove:\tRemove all containers"
    echo -e "clean:\tRemove containers and volumes (BE CAREFUL!)"
    echo ""
    echo -e "backend:\tOpen a shell inside the Flask REST API server container"
    echo -e "frontend:\tOpen a shell inside the Flask REST API server container"
    echo -e "sql:\tLaunch a sqladminer on port 8888"
    echo -e "bower:\tInstall all libraries or only the one specified"
    echo ""
    echo -e "push:\tPush code to github"
    echo -e "update:\tPull both updated code and docker images"
    echo ""
    exit 0
fi

#############################
# Check libs
if [ -z "$2" -o "$2" != "init" ]; then
    libs="../vanilla/libs/bower_components"
    out=`ls $libs 2> /dev/null | wc -m | tr -d ' '`
    if [ "$out" == "0" ]; then
        echo ""
        echo "[ERROR] You are missing JS libraries!"
        echo "Please run:"
        echo "$0 $1 init"
        exit 1
    fi
fi

#############################
# DEFAULTS FILES

# Backend
file="$1.json"
check="vanilla/specs/$file"
if [ ! -s "../$check" ]; then
    echo "File '$check' not found or empty..."
    echo "Please create it to define APIs endpoints."
    exit 1
fi
echo "{ \"$1\": \"$file\" }" > ../$apiconf

# Frontend
check="vanilla/jscode/$1"
if [ ! "$(ls -A ../$check 2> /dev/null)" ]; then
    echo "Directory '$check' not found or empty..."
    echo "Please create it to define AngularJS code."
    exit 1
fi
echo "{ \"blueprint\": \"$1\" }" > ../$jsconf


#############################
# Run services
bcom="$compose_com run $webbuild bower install"

# First time install
if [ "$2" == "init" ]; then

    echo -e "ACTION: Project init\n"
    #git remote add private
    #git@gitlab.hpc.cineca.it:mdantoni/telethon_repo.git

    echo "Download docker images"
   $compose_com $files pull
    if [ ! -d "$submodule_repo" ]; then
        echo "Clone submodules"
        cd ..
        git clone $submodule_git $submodule_repo
        cd -
    fi
    echo "Build bower packages (Javascript libraries)"
    $bcom
    echo "Completed"

elif [ "$2" == "status" ]; then
    echo -e "ACTION: Status check\n"

elif [ "$2" == "graceful" ]; then
    echo -e "ACTION: Start\n"
    $compose_com $files up -d $services

elif [ "$2" == "restart" ]; then
    echo -e "ACTION: Reboot\n"
    echo "Cleaning project containers (if any)"
    $compose_com $files stop
    $compose_com $files rm -f --all
    echo "Starting up"
    $compose_com $files up -d $services

elif [ "$2" == "stop" ]; then
    echo -e "ACTION: Stop\n"
    echo "Freezing services"
    $compose_com $files stop

elif [ "$2" == "remove" ]; then
    echo -e "ACTION: Removal\n"
    echo "Destroying services"
    $compose_com $files stop
    $compose_com $files rm -f --all

elif [ "$2" == "clean" ]; then

    echo -e "ACTION: Total removal\n"
    echo "Destroying (forever) containers & volumes. Are you really sure?"
    sleep 5
    $compose_com $files stop
    $compose_com $files rm -f --all
    for volume in `docker volume ls -q | grep $volume_prefix`;
    do
        docker volume rm $volume
        echo "Removed volume: $volume"
    done
    echo ""

elif [ "$2" == "backend" ]; then
    echo "Opening a shell inside the $2 container"
    echo "(If in debug mode, run Flask with './boot devel')"
    echo ""
    $compose_com $files exec $backend_container bash
    exit 0

elif [ "$2" == "frontend" ]; then
    echo "Opening a shell inside the $2 container"
    echo "(If in debug mode, run Flask with './boot devel')"
    echo ""
    $compose_com $files exec $fronted_container bash
    exit 0

elif [ "$2" == "sql" ]; then
    echo "Launch adminer for SQL servers"
    $compose_com run --service-ports sqladmin

elif [ "$2" == "push" ]; then

    cd ..
    echo "Pushing submodule"
    cd $submodule_repo
    git push
    if [ $? != "0" ]; then
        echo "Failed to push submodule"
        exit 1
    fi
    cd ..

    # Save a snapshot of current submodule
    echo "Save submodule status"
    echo -e \
        $(git log -n 1 --oneline --no-color)"\n"$(git branch --no-color) \
        > $submodule_tracking

    echo "Pushing main repo"
    git add $submodule_tracking
    git commit && echo "Commit has been done"

    # Push to all repos setted
    for repo in `git remote`;
    do
        git push $repo
    done

    exit 0

# Update repos, packages and images
elif [ "$2" == "update" ]; then

    $compose_com $files pull
    current=`pwd`
    cd ..

    echo "Pulling main repo"
    git pull

    echo "Pulling submodule"
    cd $submodule_repo
    git pull
    cd ..

    echo "Updating libs"
    cd $current
    $bcom

    exit 0

# Bower install
elif [ "$2" == "bower" ]; then

    if [ "$3" != "" ]; then
        bcom="${bcom} $3 --save"
        echo "Install package(s): $3"
    fi
    $bcom
else
    echo "Unknown command '$2'. Ask for help:"
    echo ""
    echo "$0 help"
    exit 0
fi

# Final check up
if [ "$?" == "0" ]; then
    if [ "$2" == "init" ]; then
        echo ""
        echo "You may launch containers now. Use:"
        echo "$0 $1 restart"
        echo ""
    else
        echo "[$1] configuration. Status:"
        $compose_com $files ps
        echo ""
        echo "Available volumes for current configuration:"
        docker volume ls | grep $volume_prefix
    fi

    if [ "$2" == 'restart' -o "$2" == 'graceful' ]; then
        echo ""
        echo "Access containers with:"
        echo "$0 $1 backend"
        echo "and/or"
        echo "$0 $1 frontend"
    fi
fi
