#!/bin/bash

###############
# Start up
shopt -s expand_aliases
source ~/.bash_aliases

###############
# Start up
if [ ! -z "SEADATA_PROJECT" ]; then

    BATCHES_PATH="/$IRODS_ZONE/$SEADATA_BATCH_DIR"
    # NOTE: we are using the main HTTP API irods user
    # to manage batches across nodes
    BATCHES_MAIN_USER="$IRODS_USER"

    berods -c "imkdir $BATCHES_PATH"
    berods -c "ichmod own $BATCHES_MAIN_USER $BATCHES_PATH"
    echo -e "Enabled the SeaDataCloud batch path: $BATCHES_PATH"

fi
