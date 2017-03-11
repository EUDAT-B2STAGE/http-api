#!/bin/bash

# GSI & certificates
add-irods-X509 guest
add-irods-X509 rodsminer admin

# # More?
# echo "Extra!"

echo -e "echo\\necho 'Become irods administrator user with the command:'\\necho '$ berods'" >> /root/.bashrc
echo -e "echo\\necho 'Switch irods GSI user then with the command:'\\necho '$ switch-gsi USERNAME'\\necho" >> /root/.bashrc
