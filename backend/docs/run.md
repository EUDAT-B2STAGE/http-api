
# Execute

The project can be executed with the command

```bash
./run.py
```

## Install requirements

Before launching please check [the requirements](../requirements.txt).

The most easiest way to install the needed packages would be using the `pip` packaging system. If you have python and pip, from a unix shell execute:

```bash
$ pip install -r requirements.txt
```

## Run with Docker

```
# from the project root directory
$ docker-compose up
```

You need `Docker` and `docker-compose` installed on your machine.

# Development options

Usage can be shown with the help flag:
```bash
$ ./run.py -h
usage: run.py [-h] [--no-security] [--debug]

REST API server based on Flask

optional arguments:
  -h, --help     show this help message and exit
  --no-security  force removal of login authentication on resources
  --debug        enable debugging mode
```

## Security mode

By default the server runs with security enabled.

To disable authentication, flask-security and flask-admin endpoints, add the
`--no-security` parameter:

```bash
$ ./run.py --no-security
restapi.app  WARNING  No security enabled! Are you sure??
```

## Debugging

Debug mode is much more verbose.
You get a lot of extra-logs and the server goes into development mode
(flask watching for file modification to restart).
Also there will be two testing endpoints for security access:

* `/api/checkuser` which verifies if your request is logged with a token
* `/api/testadmin` which verifies if your user is an admin

Enable debugging with the *debug* option:

```bash
$ ./run.py --debug
```