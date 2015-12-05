#!/bin/bash

services="backend frontend"
com="docker-compose"

cd containers
echo "Cleaning project containers (if any)"
$com stop $services
$com rm -f $services
echo "Starting up"
$com up -d $services
if [ $? == "0" ]; then
    echo "Up and running:"
    $com ps
    # docker volume ls
fi
