#!/bin/bash

services="angulask rest-mock"
com="git"
push="$com push origin master"

for service in $services;
do
    echo "Repo '$service' push"
    # Push submodules
    $push
    # Interrupt if problems appear
    if [ $? != "0" ]; then
        echo "Failed"
        exit 1
    fi
done

$com add $services
if [ "$1" == "quick" ];then
    $com commit -m 'Submodules updates'
else
    $com
fi

$push
