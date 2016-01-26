
# Developing inside the environment

We want to write REST API to do **B2SAFE** operations with python.
We will test graphdb as database backend for metadata operations (like PID).

## Writing python2 client code

The iclient container provided inside the compose is able to execute code
on the icat irods server via python.

Libraries are already installed,
(e.g. [neomodel](http://neomodel.readthedocs.org/en/latest/) and [irods python client](https://github.com/irods/python-irodsclient))
so you can write your lib inside `code` dir.

```bash
$ docker-compose up -d iclient
Starting irods_iclient_1
$ docker exec -it irods_iclient_1 bash

root@icl:/code#

# Execute your code from here. For example:

root@icl:/code# ./iclient.py

9021
/tempZone
<iRODSCollection 9022 home>
<iRODSCollection 9023 trash>
```