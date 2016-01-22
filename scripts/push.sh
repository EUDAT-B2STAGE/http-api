#!/bin/bash

services="backend"
#services="angulask rest-mock"
com="git"
push="$com push origin"
#push="$com push origin master"

###########################################
for service in $services;
do
    echo "Repo '$service' push"
    cd $service
    # Push submodules
    $push
    # Interrupt if problems appear
    if [ $? != "0" ]; then
        echo "Failed"
        exit 1
    fi
    cd ..
done

###########################################
# In case something has to be commited yet
$com add $services
# $com add *
if [ "$1" == "quick" ];then
    $com commit -m 'Submodules updates'
else
    $com commit
fi

###########################################
# Original repo
$push
# Private repo
$com push private master
