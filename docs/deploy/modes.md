
# MODES

There are two main modes to work with the HTTP-API server developed with `rapydo`. 

The main one - called `debug` - is for developers: you are expected to test, debug and develop new code. The other options is mode `production`, suited for deploying your server in a real use case scenario on top of your already running `B2SAFE` instance.

## debug mode

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


## production mode

Some important points before going further:

1. Please follow this paragraph only if you plan to deploy the HTTP API server in production, typically associated with an existing `B2SAFE` server in production.
2. Usually in production you have a domain name associated to your host IP (e.g. `b2stage-test.cineca.it` to 240.bla.bla.bla). But you can just use 'localhost' if this is not the case.
3. You may consider to register a `B2ACCESS` "app" account on the development server for the HTTP API application, to be used in the `configuration.yaml` file; otherwise the endpoint `/auth/askauth` and the related OAUTH2 based B2ACCESS authentication would not work.  

Primary step is to set up your configuration

```bash
# copy the example configuration file
$ cp projects/b2stage/example_configs/production.yaml configuration.yaml
$ vim configuration.yaml  # edit the file as suggested inside the content
```

Make sure your IRODS parameters are correctly inserted before proceding further. Deploying right after is quite simple:

```bash
# define your domain
$ DOMAIN='b2stage-test.cineca.it'
# launch production mode
$ rapydo --hostname $DOMAIN --mode production start
```

Now may access your IP or your domain and the HTTP API endpoints are online, protected by a proxy server. You can test this with:

```bash
open $DOMAIN/api/status
```

Up to now the current SSL certificate is self signed and is 'not secure' for all applications. Your browser is probably complaining for this. This is why we need to produce one with the free `letsencrypt` service.

```bash
$ rapydo --hostname $DOMAIN --mode production ssl-certificate
#NOTE: this will work only if you have a real domain associated to your IP
```

If you check again the server should now be correctly certificated. At this point the service should be completely functional.

### using the same mode for every command

To keep the production mode in every command request you can leverage the [`.projectrc`](.projectrc) file by setting the value `mode: production` inside of it.

### debugging production

In production it might be difficult to get informations if something goes wrong. If the server failed you have a couple of options to find out why:

```bash
# check any service on any mode
$ rapydo --mode YOURMODE --service YOURSERVICE log
# e.g. check all the logs from production, following new updates
# $ rapydo --mode production log --follow

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

