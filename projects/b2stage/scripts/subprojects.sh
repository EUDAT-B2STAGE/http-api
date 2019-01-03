#!/bin/bash

###############
# Start up
shopt -s expand_aliases
source ~/.bash_aliases

###############
# Start up
if [ ! -z "SEADATA_PROJECT" ]; then

    BATCHES_PATH="/$IRODS_ZONE/$SEADATA_INGESTION_COLL"
    PROD_PATH="/$IRODS_ZONE/$SEADATA_PRODUCTION_COLL"
    ORDERS_PATH="/$IRODS_ZONE/$SEADATA_ORDERS_COLL"

    # NOTE: we are using the main HTTP API irods user
    # to manage batches across nodes
    BATCHES_MAIN_USER="$IRODS_USER"

    berods -c "imkdir $BATCHES_PATH"
    berods -c "ichmod own $BATCHES_MAIN_USER $BATCHES_PATH"
    echo -e "Enabled the SeaDataCloud path: $BATCHES_PATH"

    berods -c "imkdir $PROD_PATH"
    berods -c "ichmod own $BATCHES_MAIN_USER $PROD_PATH"
    echo -e "Enabled the SeaDataCloud path: $PROD_PATH"

    berods -c "imkdir $ORDERS_PATH"
    berods -c "ichmod own $BATCHES_MAIN_USER $ORDERS_PATH"
    echo -e "Enabled the SeaDataCloud path: $ORDERS_PATH"

fi
