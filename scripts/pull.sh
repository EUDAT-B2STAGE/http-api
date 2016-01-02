#!/bin/bash

services="backend"
#services="angulask rest-mock"
com="git"
pull="$com pull origin master"

$pull

for service in $services;
do
    echo "Repo '$service'"
    $pull
done

# echo "Submodule sync"
# git submodule sync
# git submodule update
