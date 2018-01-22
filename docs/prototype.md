
# Prototype

Hello EUDAT user!

The first release candidate was created.

Before getting our hands on the first `HTTP-API` server prototype, here's a list of key points to consider:

- You need `B2ACCESS` credentials as an EUDAT user inside the [development instance](https://unity.eudat-aai.fz-juelich.de:8443/home/).
- B2SAFE/irods credentials do not work as HTTP API credentials at the moment.
- The current instance is working on a testbed B2SAFE running at [CINECA](http://hpc.cineca.it/).

The HTTP API prototype endpoints are accessible through the following two URI prefixes:

- `SERVER/api`
- `SERVER/auth`

(for example to authenticate you need to `POST` credentials at: https://b2stage-test.cineca.it/auth/b2safeproxy)

## Status

The status page for the current prototype is:
https://b2stage-test.cineca.it/api/status

This is the endpoint to call if you want to automatically verify if the server is responding to request. 

<!--
This endpoint is also automatically monitored from the [uptime robot service](https://stats.uptimerobot.com/xGG9gTK3q).
-->

## List of available endpoints

How do we understand which endpoint we need to call and which require authentication?

The EUDAT B2STAGE HTTP API provide description of up-to-date specifications following the latest version (`3.0`) of the `openapi` standard from [Swagger](https://swagger.io/specification/). 

The description in `JSON` format is available at:
https://b2stage-test.cineca.it/api/specs


## Clients

### authentication process

Details on how to create a valid token upon the current release of the HTTP API is available [inside the user guide](user/authentication.md).

### curl

See also the [main user page](user/user.md) to understand which endpoints exists and how to use them from command line/terminal with the `curl` application.

### official swagger-ui website

Since the HTTP API server follows the `openapi` standard, you can query its endpoints also using the official `swagger-ui` web server, by just passing the `JSON` file in input:

[link to the swagger `petstore`](http://petstore.swagger.io/?url=https://b2stage-test.cineca.it/api/specs&docExpansion=none)

### python client

You can find a [dedicated python module file](data/scripts/templates/client.py) to query the EUDAT B2STAGE HTTP-API. 

The script is already configured to work with a local deploy of the HTTP-API containers on your computer or to a remote host. Before using it open the file and [change](https://github.com/EUDAT-B2STAGE/http-api/blob/master/data/scripts/templates/client.py#L22-L23) the basic [parameters](https://github.com/EUDAT-B2STAGE/http-api/blob/master/data/scripts/templates/client.py#L27).

#### local

If you are [running a working copy]() of the `B2STAGE HTTP-API` you can test the client by simply calling from a `UNIX` terminal:

```bash
data/scripts/templates/client.py
```

#### remote

If you have credentials to a remote instance of the `HTTP-API` you just need to provide them inside the script and then execute with:

```bash
data/scripts/templates/client.py --remote
```
