#!/bin/bash

services="backend"
#services="angulask rest-mock"
com="git"
pull="$com pull"

$pull

for service in $services;
do
    echo "Repo '$service'"
    $pull
    git pull origin master
done

# echo "Submodule sync"
# git submodule sync
# git submodule update
