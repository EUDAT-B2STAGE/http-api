# Authentication 

To authenticate access to the B2SATGE HTTP-API service, you must first register a new B2ACCESS account (see https://b2access.eudat.eu:8443/home/home).
Credentials are a combination of your user name and password: they are needed to generate authentication tokens.
When you send API requests, you include the token in the X-Auth-Token header. A token is valid for a limited time before it expires. A token can also become invalid for other reasons. For example, if existing tokens for that user are no longer valid.


## B2ACCESS Authorization 

The B2STAGE HTTP-API uses the OAuth2 authorization framework to obtain limited access to B2ACCESS user accounts. It works by delegating user authentication to the service that hosts the user account (B2ACCESS), and authorizing third-party applications (B2STAGE HTTP-API) to access the user account. 

To allow the B2STAGE HTTP-API to access user's account, visit the following URL via a web browser and click on "authorize application":

'http://<http_server:port>/auth/askauth'

[describe the full workflow]

This is a one-time operation, needed only the first time you need to get access to the B2STAGE HTTP-API.

## Authentication and API request workflow

To send any kind of request to the B2STAGE HTTP-API an authenitcation token is needed.
To request an authentication token send your B2ACCESS  credentials in the request as shown in Authenticate. If the request succeeds, the server returns an authentication token.

Once you obtain a valid authentication token user can send HTTP requests including the token in the X-Auth-Token header. Continue to send API requests with that token until the service completes the request or the Unauthorized (401) error occurs.

If the Unauthorized (401) error occurs, request another token.

The examples in this section use cURL commands. For information about cURL, see http://curl.haxx.se/.

## Authenitcation

The payload of credentials to authenticate contains these parameters:

| Parameter | Type | Description |
|---------------------|--------|------------------------------------------------------------------------------------------------|
| username (required) | string | The EUDAT user name. If you do not have one, register a new account on the B2ACCESS user portal |
| password (required) | string | The password for the user. |

To request a token run this cURL command:

```
$ curl -s -X POST http://<http_server:port>/auth/authorize \
  -H "Content-Type: application/json"
```