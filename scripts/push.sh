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
# $com add $services
# $com add *

# Save a snapshot of current submodule
echo "Save submodule status"
echo -e \
    $(git show --pretty=%H)"\n"$(git show-branch --current --no-color) \
    > $submodule_tracking

echo "Pushing main repo"
git add $submodule_tracking
git commit && echo "Commit has been done"

###########################################
# Push to all repos setted

for repo in `git remote`;
do
    git push $repo
done
