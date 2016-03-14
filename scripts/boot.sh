#!/bin/bash

echo "# ############################################ #"
echo -e "\t\tRestangulask"
echo "# ############################################ #"
echo ""

#############################
# Defaults
apiconf="vanilla/specs/api_init.json"
jsconf="vanilla/specs/js_init.json"

#############################
# Other variables
com="docker-compose"
#services="backend frontend"
services="custombe customfe"
webbuild="bower"
volume_prefix="restangulask_"

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

# TO FIX: add custom compose here too

    docker-compose pull
    current=`pwd`
    cd ..
    for service in $services;
    do
        echo "Repo '$service' fetch"
        cd $service
        git pull
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

    if [ -z "$1" ]; then
        echo "Please specify one configuration to use."
        echo "Available configurations:"
        for i in `ls custom`;
        do
            name=`echo $i | sed "s/\.yml//"`
            echo -e "\t$name"
        done
        exit
    fi

    #############################
    # Check compose stack existence
    file="custom/${1}.yml"
    if [ ! -f "$file" ]; then
        echo "File 'containers/$file' not found!"
        echo "You might start up copying 'template.yml'."
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

    #############################
    # Case you ask for base 'template'
    if [ "$1" == "template" ]; then
        touch ../$apiconf
        echo "{ \"blueprint\": \"blueprint_example\" }" > ../$jsconf

    #############################
    # DEFAULTS FILES
    else
        # Backend
        file="$1.ini"
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
    fi

    #############################
    # Run services if not adding another command
    if [ -z "$2" ]; then
        echo -e "ACTION: Reboot\n"
        echo "Cleaning project containers (if any)"
        $com $files stop
        $com $files rm -f
        echo "Starting up"
        $com $files up -d $services
    else
        if [ "$2" == "start" ]; then
            echo -e "ACTION: Start\n"
            $com $files up -d $services
        fi
        if [ "$2" == "stop" ]; then
            echo -e "ACTION: Stop\n"
            echo "Freezing services"
            $com $files stop
        fi
        if [ "$2" == "remove" ]; then
            echo -e "ACTION: Removal\n"
            echo "Destroying services"
            $com $files stop
            $com $files rm -f
        fi
    fi
    # Check up
    if [ "$?" == "0" ]; then
        echo "[$1] configuration. Status:"
        $com $files ps
        echo ""
        echo "Available volumes"
        docker volume ls | grep $volume_prefix
    fi
fi
