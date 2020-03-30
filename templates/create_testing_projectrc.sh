#!/bin/bash

touch .projectrc
cat <<EOF > .projectrc
project: ${PROJECT}
project_configuration:
  variables:
    env:
      IRODS_ANONYMOUS: 1
      ENABLE_PUBLIC_ENDPOINT: 1
      ACTIVATE_TESTING_MODE: 1
EOF
