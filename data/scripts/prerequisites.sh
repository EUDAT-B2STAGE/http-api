#!/bin/bash

USER_OPTION=""
if [ ! "$TRAVIS" == "true" ]; then
    USER_OPTION="--user"

for existing in `pip3 list --format columns | grep rapydo | awk '{print $1}'`;
do
    echo "removing: $existing"
    pip3 uninstall -y $existing
done

if [ "$1" == 'dev' ]; then
    files="*requirement*txt"
else
    files="requirement*txt"
fi

for package in `cat projects/*/$files`;
do
    echo "adding: $package"
    pip3 install $USER_OPTION --upgrade $package
done
