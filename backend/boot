#!/bin/bash

main_command="./run.py"

# Init variables
if [ "$1" == "devel" ]; then
    APP_MODE='development'
elif [ "$APP_MODE" == "" ]; then
    APP_MODE='production'
fi

# Select the right option
if [ "$APP_MODE" == "debug" ]; then
    echo "[=== DEBUG MODE ===]"
    sleep infinity
elif [ "$APP_MODE" == "production" ]; then
    echo "Production !"
## GUNICORN?
    $main_command
else
    echo "Development"
    # API_DEBUG="true" $main_command
    $main_command --debug
fi
