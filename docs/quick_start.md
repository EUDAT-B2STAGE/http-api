
# Quick start

This is a reference page to quick start your knowledge of the HTTP API project; by reading this page you may get a first insight on how this project works.


## Feedback on the first Release Candidate

To gather into one place the feedback of any user testing a deployed HTTP API server or the online prototype, we created a dedicated free chat room on the `gitter` comunication platform:

https://gitter.im/EUDAT-B2STAGE/http-api

Please: feel free to report or comment to help us improve!


## Using the prototype online

If you don't want to deploy or develop the current project state, you may test online our [prototype](https://b2stage.cineca.it/api/status). If that is the case see the [dedicated instructions](prototype.md).


## Deployment pre-requisites

In order to deploy this project you need to install the `RAPyDO controller` and use it to startup the services on a `Docker` environment with containers.

The following instruction are based on the hyphotesis that you will work on a `UNIX`-based OS. Any `Linux` distributions (Ubuntu, CentOS, Fedora, etc.) or any version of `Mac OSX` will do. Command line examples were heavily tested on `bash` terminal (version `4.4.0`, but also version `3.x` should work).

Please note that for installing tools into your machine the suggested option is through your preferred OS package manager (e.g. `apt`, `yum`, `brew`, etc.).


### Base tools

- The `git` client. 
 
Most of UNIX distributions have it already installed. If that is not that case then refer to the [official documentation]()

- The `python 3.4+` interpreter installed together with its main package manager `pip3`.

Most of distributions comes bundled with `python 2.7+`, which is not suitable for our project. Once again use a package manager, for example in ubuntu you would run:

```bash
$ apt-get update && apt-get install python3-pip
```


### Containers environment

#### docker engine

To install docker on a unix terminal you may use the [get docker script](https://get.docker.com):

```
# Install docker
$ curl -fsSL get.docker.com -o get-docker.sh
$ sh get-docker.sh
```

For Mac and Windows users dedicated applications were written: 

- [Docker for Mac](https://www.docker.com/docker-mac)  
- [Docker for Windows](https://www.docker.com/docker-windows)

As alternative, the best way to get Docker ALL tools working
is by using their [toolbox](https://www.docker.com/toolbox).

#### docker compose

`Compose` is a tool for docker written in Python. See the [official instructions](https://docs.docker.com/compose/install/) to install it.

NOTE: compose comes bundled with the toolbox.


## Start-up the project

Here's a step-by-step tutorial to work with the HTTP API project.


### 1. cloning 

To clone the working code:

```bash
$ VERSION=0.6.0 \
    && git clone https://github.com/EUDAT-B2STAGE/http-api.git \
    && cd http-api \
    && git checkout $VERSION  

# now you will have the current latest release (RC1)
```


### 2. configure

Now that you have all necessary software installed, before launching services you should consider editing the main configuration:

[`projects/eudat/project_configuration.yaml`](projects/eudat/project_configuration.yaml)

Here you can change at least the basic passwords, or configure access to external service (e.g. your own instance of iRODS/B2SAFE) for production.


### 3. controller

The controller is what let you manage the project without much effort.
Here's what you need to use it:

```bash
# install and use the rapydo controller
$ data/scripts/prerequisites.sh 
# you have now the executable 'rapydo'
$ rapydo --version
# If you use a shell different from bash (e.g. zsh) 
# you can try also the short alias 'do'
$ do --help
```

NOTE: python install binaries in `/usr/local/bin`. If you are not the admin/`root` user then the virtual environment is created and you may find the binary in `$HOME/.local/bin`. Make sure that the right one of these paths is in your `$PATH` variable, otherwise you end up with `command not found`.


### 4. deploy initialization

Your current project needs to be initialized. This step is needed only the first time you use the cloned repository.

```bash
$ rapydo init
```

NOTE: with `RC1` there is no working `upgrade` process in place to make life easier if you already have this project cloned from a previous release. This is something important already in progress [here](https://github.com/EUDAT-B2STAGE/http-api/issues/87).

If you wish to __**manually upgrade**__:

```bash
VERSION="0.6.1"
git checkout $VERSION

# supposely the rapydo framework has been updated, so you need to check:
rm -rf submodules/*
data/scripts/prerequisites.sh
rapydo init

# update docker images with the new build templates in rapydo
# NOTE: select your mode based on the next paragraph
rapydo --mode YOURMODE build -r -f
```

### 5. MODES

There are two main modes to work with the API server. The main one - called `debug` - is for developers: you are expected to test, debug and develop new code. The other options is mode `production`, suited for deploying your server in a real use case scenario on top of your already running `B2SAFE` instance.

#### debug mode

NOTE: follow this paragraph only if you plan to develop new features on the HTTP API.

```bash
################
# bring up the docker containers in `debug` mode
$ rapydo start
# NOTE: this above is equivalent to default value `do --mode debug start`

# laungh the restful http-api server 
$ rapydo shell backend --command 'restapi launch'
# or
$ rapydo shell backend 
[container shell]$ restapi launch
```

NOTE: the block of commands above can be used at once with:

```bash
$ rapydo start --mode development
# drawback: when the server fails at reloading, it crashes
```


And now you may access a client for the API, from another shell and test the server:

```bash
$ rapydo shell restclient
```

The client shell will give you further instructions on how to test the server. In case you want to log with the only existing admin user:

- username: user@nomail.org
- password: test

NOTE: on the client image you have multiple tools installed for testing:
- curl
- httpie
- http-prompt


#### production mode

Some important points before going further:

1. Please follow this paragraph only if you plan to deploy the HTTP API server in production
2. Usually in production you have a domain name associated to your host IP (e.g. `b2stage.cineca.it` to 240.bla.bla.bla). But you can just use 'localhost' if this is not the case.
3. You need a `B2ACCESS` account on the development server for the HTTP API application. Set the credentials [here](https://github.com/EUDAT-B2STAGE/http-api/blob/0.6.0/projects/eudat/project_configuration.yaml#L22-L26) otherwise the endpoint `/auth/askauth` would not work.  

Deploying is very simple:

```bash
# define your domain
$ DOMAIN='b2stage.cineca.it'
# launch production mode
$ rapydo --host $DOMAIN --mode production start
```

Now may access your IP or your domain and the HTTP API endpoints are online, protected by a proxy server. You can test this with:

```bash
open $DOMAIN/api/status
```

Up to now the current SSL certificate is self signed and is 'not secure' for all applications. Your browser is probably complaining for this. This is why we need to produce one with the free `letsencrypt` service.

```bash
$ rapydo --host $DOMAIN --mode production ssl-certificate
#NOTE: this will work only if you have a real domain associated to your IP
```

If you check again the server should now be correctly certificated. At this point the service should be completely functional.

In production it might be difficult to get informations if something goes wrong. If the server failed you have a couple of options to find out why:

```bash
# check any service on any mode
$ rapydo --mode YOURMODE --service YOURSERVICE log
# e.g. check all the logs from production, following new updates
$ rapydo --mode production log --follow

## if this is not enough:

# check the backend as admin of the container
$ rapydo shell --user root backend
# look at the production WSGI logs
less /var/log/uwsgi/*log
# check processes
ps aux --forest
# here uwsgi (as developer) and nginx (as www-data) should be running 

## if you only get 'no app loaded' from uWSGI, 

$ rapydo shell backend
# launch by hand a server instance
$ DEBUG_LEVEL=VERY_VERBOSE restapi launch
# check if you get any error in your output

```

Also please take a look at how to launch interfaces in the upcoming paragraph, in case there is a problem with the database or swagger.


## Other operations

Here we have more informations for further debugging/developing the project


### launch interfaces

To explore data and query parameters there are few other services as options:

```bash
SERVER=localhost  # or your IP / Domain
PORT=8080

# access a swagger web ui
rapydo interfaces swagger
# access the webpage:
open http://$SERVER/swagger-ui/?url=http://$SERVER:$PORT/api/specs

# SQL admin web ui
rapydo interfaces sqlalchemy
# access the webpage:
open http://$SERVER:81/adminer
```

### add valid b2handle credentials

To resolve non-public `PID`s prefixes for the `EPIC HANDLE` project we may leverage the `B2HANDLE` library providing existing credentials. 

You can do so by copying such files into the dedicated directory:

```bash
cp PATH/TO/YOUR/CREDENTIALS/FILES/* data/b2handle/
```

### destroy all

If you need to clean everything you have stored in docker from this project:

```bash
# BE CAREFUL!
rapydo clean --rm  # very DANGEROUS
# With this command you lose all your current data!
```

### hack the certificates volume

This hack is necessary if you want to raw copy a Certification Authority credential. 
It may be needed if your current B2SAFE host DN was produced with an internal certification authority which is not recognized from other clients.

```bash
path=`docker inspect $(docker volume ls -q | grep sharedcerts) | jq -r ".[0].Mountpoint"`
sudo cp /PATH/TO/YOUR/CA/FILES/CA-CODE.* $path/simple_ca

```
