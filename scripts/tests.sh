#!/bin/bash

echo "Launching tests with coverage"
sleep 1

# Avoid colors when saving tests output into files
export TESTING_FLASK="True"

# nosetests \
#     --stop \
#     --with-coverage \
#     --cover-erase --cover-package=rapydo \
#     --cover-html --cover-html-dir=/tmp/coverage

# Coverage + stop on first failure
com="nose2 -F"
option="-s test"
cov_reports=" --coverage-report term --coverage-report html"

# cov_options="--output-buffer -C --coverage rapydo --coverage flask_ext"
# if [ ! -z "$VANILLA_PACKAGE" ]; then
#     echo "Extra coverage for project '$VANILLA_PACKAGE'"
#     cov_options="$cov_options --coverage $VANILLA_PACKAGE"
# fi

cov_options="--output-buffer -C --coverage ${VANILLA_PACKAGE}.apis"

echo $com $cov_options $cov_reports

# Basic tests, written for the http-api-base sake
$com $option/base --log-capture
if [ "$?" == "0" ]; then
    # Custom tests from the developer, if available
    $com $option/custom --log-capture
    if [ "$?" == "0" ]; then
        # Print coverage if everything went well so far
        $com $cov_options $cov_reports 2> /tmp/logfile.txt
        grep "platform linux" -A 1000 /tmp/logfile.txt
    else
        exit $?
    fi
else
    exit $?
fi
