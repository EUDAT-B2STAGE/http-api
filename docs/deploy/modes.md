# MODES #

There are two main modes to work with the HTTP-API server developed with `rapydo`.

The main one - called `development` - is for developers: you are expected to test, debug and develop new code. The other options is `production`, suited for deploying your server in a real use case scenario on top of your already running `B2SAFE` instance.

## development mode ##

NOTE: follow this paragraph only if you plan to develop new features on the HTTP API.

```bash
# bring up the docker containers in `debug` mode
$ rapydo start
# NOTE: this above is equivalent to default value `do --mode debug start`

# laungh the restful http-api server
$ rapydo shell backend --command 'restapi launch'
# or
$ rapydo shell backend
[container shell]$ restapi launch
```

## production mode

Some important points before going further:

1. Please follow this paragraph only if you plan to deploy the HTTP API server in production, typically associated with an existing `B2SAFE` server in production.
2. Usually in production you have a domain name associated to your host IP (e.g. `b2stage-test.cineca.it` to 240.bla.bla.bla). But you can just use 'localhost' if this is not the case.
3. You may consider to register a `B2ACCESS` "app" account on the development server for the HTTP API application, to be used in the `configuration.yaml` file; otherwise the endpoint `/auth/askauth` and the related OAUTH2 based B2ACCESS authentication would not work.

Primary step is to set up your configuration

```bash
# copy the example configuration file
$ cp templates/projectrc.yml .projectrc.yml
$ vim configuration.yaml  # edit the file as suggested inside the content
```

Make sure your IRODS parameters are correctly inserted before proceding further. Deploying right after is quite simple:

```bash
# options are in .projectrc.yml
$ rapydo start
# this is equivalent to 
$ rapydo --project b2stage --production --hostname b2stage.yourdomain.io start
```

Now may access your IP or your domain and the HTTP API endpoints are online, protected by a proxy server. You can test this with:

```bash
open $DOMAIN/api/status
```

Up to now the current SSL certificate is self signed and is 'not secure' for all applications. Your browser is probably complaining for this. This is why we need to produce one with the free `letsencrypt` service.

```bash
# NOTE: this will work only if you have a real domain associated to your IP
$ rapydo ssl
```

If you check again the server should now be correctly certificated. At this point the service should be completely functional.


### debugging production

In production it might be difficult to get informations if something goes wrong. If the server failed you have a couple of options to find out why:

```bash
# check any service on any mode
$ rapydo --services YOURSERVICE logs
# e.g. check all the logs from production, following new updates
# $ rapydo logs --follow

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
$ LOGURU_LEVEL=VERBOSE restapi launch
# check if you get any error in your output

```

Also please take a look at how to launch interfaces in the upcoming paragraph, in case there is a problem with the database or swagger.

