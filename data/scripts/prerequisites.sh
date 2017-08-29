#!/bin/bash

vename="b2stage"
myuser=$(whoami)

# use virtualenv
if [ $myuser != "root" ]; then
    echo "You are not the administrator."
    echo "Switching to a virtual environment."
    echo ""
    pip3 install --user virtualenv
    ve="$HOME/.local/bin/virtualenv"
    $ve $vename
    source $vename/bin/activate
fi

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
    pip3 install --upgrade $package
done

if [ $myuser != "root" ]; then
    echo "Please activate the environment with:"
    echo "source $vename/bin/activate"
fi

branch=$(git rev-parse --abbrev-ref HEAD)
link="https://github.com/EUDAT-B2STAGE/http-api/blob/$branch/docs/quick_start.md"
echo "To work with this project please check first instructions:"
echo $link
