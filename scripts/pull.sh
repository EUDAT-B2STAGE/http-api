#!/bin/bash

services="angulask rest-mock"
com="git"
pull="$com pull"

for service in $services;
do
    echo "Repo '$service'"
    $pull
done

$pull

echo "Submodule sync"
git submodule sync
git submodule update
