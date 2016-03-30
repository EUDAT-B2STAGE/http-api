
# Developing inside the environment

We want to write REST API to do **B2SAFE** operations with python.
We will test graphdb as database backend for metadata operations (like PID).

## Adding another user into the irods server

Based on the GSI plugin, you may create a new valid X509 certificate
for a new user, and add it to the irods system with our script:

```bash
$ scripts/run.sh addiuser tester

Created a valid signed certificate: /opt/certificates/tester/usercert.pem
Check certificate:
subject= /O=Grid/OU=GlobusTest/OU=simpleCA-0039b2bbc9c5/OU=Globus Simple CA/CN=tester
Added certificate for user 'tester' to irods authorizations

Check users and certificates:
guest /O=Grid/OU=GlobusTest/OU=simpleCA-0039b2bbc9c5/OU=Globus Simple CA/CN=guest
tester /O=Grid/OU=GlobusTest/OU=simpleCA-0039b2bbc9c5/OU=Globus Simple CA/CN=tester
```

## Writing python client code

The `rest` container provided inside the compose is able to execute code
on the icat irods server via python.

Libraries are already installed,
(e.g. [neomodel](http://neomodel.readthedocs.org/en/latest/) and [irods python client](https://github.com/irods/python-irodsclient))
so you can write your lib inside `code` dir.

Note: since **irods python client** is not working with python3 at the time
of writing, we are just using icommands wrappers for now...

```bash
# Launch the instances
$ scripts/run.sh graceful
# Open the shell
$ scripts/run.sh server_shell

# Execute your code from here. For example:

irods@api:/code/project$ ./boot devel
```