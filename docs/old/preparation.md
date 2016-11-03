# Preparing our docker environment

## Initialization
These operations are needed only the first time you run the containers.

### Data persistence

Containers do not store modifications once started.

There are many ways to achieve persistence; the most common patterns are: mounting an external directory or either using the **datacontainer** pattern. But we will not use them.

Since Docker 1.9 (the most recent at the time of writing) you may create volumes with specific names (and drivers) to save data to persist (e.g. libs/data for your Database, or configurations for your server).

Our environment will require different volumes with specific names. **Docker compose** let you specify the name inside the YAML file,
they will be automatically created.

To check your current existing volumes:
```bash
$ docker volume ls
DRIVER              VOLUME NAME
local               thisismyvolume
```

We will talk about our volumes again at the end of this chapter.

### Database

The postgresql docker image is (of course) with empty data.
To create user and database, and allow the irods user to access, use the following:
```bash
# Launching db service init in background (-d option)
docker-compose -f docker-compose.yml -f init.yml up -d sql
```

The above operation needs 5/10 seconds to boost.
If you want to verify what is happening,
compose let you check logs of running containers. E.g.:
```bash
docker-compose logs sql
# press CTRL-c when you see everything is configured
```


### iRODS configuration

iRODS server image is ready to be installed and configured,
but needs to be linked to an existing database.

Before launching the next installation script,
you should provide your EPIC Handle credentials inside the file
`confs/credentials.conf`: needed for enabling the
**Persistent IDentifier (PID)** onto your instance.

Please provide the following variables:

`
HANDLE_BASE=""      # epic base url
HANDLE_USER=""      # your username for previous url
HANDLE_PREFIX=""    # prefix for base url
HANDLE_PASS=""      # password for previous user
`

Once you modified that file, if you created the database and username inside the previous paragraph, you are ready to create your instance of this service with the command:
```bash
docker-compose -f docker-compose.yml -f init.yml up icat
# note: we don't leave this operation in background
# it will say "Connected" when everything has gone fine
# [...]
icat_1 | Connected
irods_icat_1 exited with code 0
```

If you completed this step with no errors, you may already proceed to the
[next chapter](running.md).

### Your volumes

Now that you have prepared the services, you should also have all the docker volumes in place:

```bash
$ docker volume ls
DRIVER              VOLUME NAME
local               httpapi_sqldata
local               httpapi_restlitedb
local               httpapi_eudatopt
local               httpapi_irodshome
local               httpapi_etcconf
local               httpapi_irodsvar
local               httpapi_sharedcerts
```

As you may notice, every volume used in this project starts with
the prefix `httpapi_`, to make easier to find them.

### Debugging database link

In case you have DB problems and you really need to debug the connection from the icat container to the postgres db you could try with:
```bash
$ docker-compose up -d
$ docker exec -it irods_icat_1 bash
$ psql -h db -W -d ICAT
# enter password

psql (9.4.5)
ICAT=#
# if you arrive here, database linking is fine.
# do some other database checks
```

Also you can refer to the [admin chapter](admin.md) to access the database with a web interface.
