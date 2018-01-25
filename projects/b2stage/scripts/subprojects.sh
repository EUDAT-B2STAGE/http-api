#!/bin/bash

###############
# Start up
shopt -s expand_aliases
source ~/.bash_aliases

###############
# Start up
if [ ! -z "SEADATA_PROJECT" ]; then

    BATCHES_PATH="/$IRODS_ZONE/$SEADATA_BATCH_DIR"
    # FIXME: who should be here?
    BATCHES_MAIN_USER='anonymous'

    berods -c "imkdir $BATCHES_PATH"
    berods -c "ichmod own $BATCHES_MAIN_USER $BATCHES_PATH"
    echo -e "Enabled the SeaDataCloud batch path: $BATCHES_PATH"

fi
