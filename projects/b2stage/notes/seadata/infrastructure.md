
# Infrastructure


## instructions

0. HTTP API irods user has to be an "irods adminer"
1. install Rancher and add at least one nodes
2. generate API keys for the HTTP API
3. configure Rancher to access the private docker hub/registry
4 add labels to host(s) that will run quality checks
    + host_type=qc

- TODO: clean up once a day with the Janitor in the catalog
    + https://github.com/rancher/community-catalog/tree/master/templates/janitor

<!--
- launch from the catalog an NFS server
    + mount the NFS server folder as a zone in irods server
    + mount the NFS server to every host that will run quality checks 
        in /usr/share/inputs
-->
