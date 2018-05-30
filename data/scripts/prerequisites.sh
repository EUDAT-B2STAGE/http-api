#!/bin/bash

# pip_binary="pip3"
pip_binary="pip3 --disable-pip-version-check"
ve_name="b2stage"
myuser=$(whoami)

# use virtualenv
if [ $myuser != "root" ]; then
    echo "You are not the administrator!"
    echo ""
    echo "Switching to a Python virtual environment (with virtualenv)."
    echo ""
    $pip_binary install --user virtualenv
    ve="$HOME/.local/bin/virtualenv"
    $ve $ve_name
    source $ve_name/bin/activate
fi

#############################
## PIP 10 BROKEN UPDATE
## see: https://github.com/pypa/pip/issues/5221

# # update or die
# $pip_binary install --upgrade pip
# if [ "$?" != 0 ]; then
#     echo "Failed to use $pip_binary. Did you install Python and Pip?"
# fi

## if broken, try:
## $ python3 -m pip install --force-reinstall pip
#############################

for existing in `$pip_binary list | grep rapydo | awk '{print $1}'`;
do
    echo "removing: $existing"
    $pip_binary uninstall -y $existing
done

if [ "$1" == 'dev' ]; then
    files="*requirement*txt"
else
    files="requirement*txt"
fi

for package in `cat projects/*/$files`;
do
    echo "adding: $package"
    $pip_binary install --upgrade $package
done

if [ $myuser != "root" ]; then
    echo "Please activate the environment with:"
    echo "source $ve_name/bin/activate"
fi

branch=$(git rev-parse --abbrev-ref HEAD)
echo "======="
echo
link="https://github.com/EUDAT-B2STAGE/http-api/blob/$branch/docs/quick_start.md"
echo "To work with this project please check first instructions:"
echo $link
echo
