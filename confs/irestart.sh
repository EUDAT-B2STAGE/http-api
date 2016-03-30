#!/bin/bash

yes $IRODS_PASS | sudo -S /etc/init.d/irods restart
