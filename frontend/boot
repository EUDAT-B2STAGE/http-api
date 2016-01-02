#!/bin/bash

main_command=" ./app.py"

if [ "$1" == "devel" ]; then
    APP_MODE='development'
elif [ "$APP_MODE" == "" ]; then
    APP_MODE='production'
fi

echo -n -e "#BOOTSTRAP bash:\t"

if [ "$APP_MODE" == "debug" ]; then
    echo "[=== DEBUG MODE ===]"
    sleep infinity
elif [ "$APP_MODE" == "production" ]; then
    echo "[=== PRODUCTION MODE ===]"
## NGINX + WSGI?
    FLASK_CONFIGURATION="$APP_MODE" APP_DEBUG="false" $main_command
else
    echo "[=== DEVELOPMENT MODE ===]"
    FLASK_CONFIGURATION="$APP_MODE" APP_DEBUG="true" $main_command
fi


##########################################
## OLD EXPERIMENTS

# # Activate virtual env
# echo "Enabling python environment"
# . /opt/venv/bin/activate

# if [ "$1" == "production" ];
# then
#     #### # NORMAL APP
#     echo "Activate nginx"
#     /etc/init.d/nginx start
#     echo "Uwsgi app"
#     uwsgi --ini /etc/uwsgi/vassals/uwsgi.ini
# else
#     ### # TEST irods and graphdb
#     echo "Waiting for irods to be started"
#     sleep 30
#     curl -i -X POST \
#         http://neo4j:neo4j@neo:7474/user/neo4j/password \
#         -d 'password=test'
#     yes test | iinit
#     python /app/run.py
# fi
##########################################
