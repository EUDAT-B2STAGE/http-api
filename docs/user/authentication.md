# Authentication and API request workflow 

The B2STAGE HTTP-API uses the OAuth2 authorization framework to obtain limited access to B2ACCESS user accounts. It works by delegating user authentication to the service that hosts the user account (B2ACCESS), and authorizing third-party applications (B2STAGE HTTP-API) to access the user account. 

Therefore, to access to the B2SATGE HTTP-API service, you must first register a new **B2ACCESS** account and [get valid credentials](https://b2access.eudat.eu:8443/home/home).


## B2ACCESS Authorization 

Credentials are a combination of your user name and password: they are needed to generate authentication tokens.

To allow the B2STAGE HTTP-API to access B2ACCESS user's account, visit the following URL via a web browser and click on "authorize application":

'http://<http_server:port>/auth/askauth'

[describe the full workflow]
You will redirect to 'http://<http_server:port>/auth/authorization' where you will be prompted to authorize the B2SATGE HTTP-API application.

This is a one-time operation, needed only the first time you need to get access to the B2STAGE HTTP-API.

## Authentication

To send any kind of requests to the B2STAGE HTTP-API an authentication token is needed:

1. to request an authentication token the B2ACCESS credentials has to be sent in the request as shown in [Login](#login). If the request succeeds, the server returns an authentication token;

2. once you obtain a valid authentication token user can send HTTP requests including the token in the X-Auth-Token header. Continue to send API requests with that token until the service completes the request or the Unauthorized (401) error occurs;

3. if the Unauthorized (401) error occurs, request another token (see point 1).

The examples in this section use cURL commands. For information about cURL, see http://curl.haxx.se/.

##Login

This section shows how to obtain a valid authentication token needed to send requests to the B2STAGE HTTP-API.

### Parameters:

| Parameter | Type | Description 
|-----------|------|-------------
| username (required) | string | The EUDAT user name. If you do not have one, register a new account on the B2ACCESS user portal 
| password (required) | string | The password for the user. 

To request a token run this cURL command:
```bash
$ curl -u <username>:<password> http://<http_server:port>/auth/login 
```

### Response 

If the request succeeds, a successful response containing the authentication token will be returned, as in the following example:

```json
[response example]
```

## Send API requests

This section shows how to make a basic API call. For a complete list of API calls, see API.

Every API request must contain a valid authentication token obtained using the Login API.
An example of API request is the following: 

```bash
$ curl http://<http_server:port>/api/status -H "Authorization: Bearer <auth_token>"
```
