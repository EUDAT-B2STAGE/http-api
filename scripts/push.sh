#!/bin/bash

services="backend"
#services="angulask rest-mock"
submodule_tracking="submodules.current.commit"

###########################################
for service in $services;
do
    echo "Repo '$service' push"
    cd $service
    # Push submodules
    git push
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

    # Save a snapshot of current submodule
    echo "Save submodule status"
    echo -e \
        $(git show --pretty=%H)"\n"$(git show-branch --current --no-color) \
        > $submodule_tracking

    echo "Pushing main repo"
    git add $submodule_tracking
    git commit && git push && echo "Completed"
fi

###########################################
# Original repo
$push

# Private repo
$com push private master
