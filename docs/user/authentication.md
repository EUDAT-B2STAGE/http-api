# Authentication and API request workflow 

The B2STAGE HTTP-API uses the OAuth2 authorization framework to obtain limited access to B2ACCESS user accounts. It works by delegating user authentication to the service that hosts the user account (B2ACCESS), and authorizing third-party applications (B2STAGE HTTP-API) to access the user account. 

Therefore, to use the B2SATGE HTTP-API service, you must first register a new **B2ACCESS** personal account and [get valid credentials](https://b2access.eudat.eu:8443/home/home).

## Authentication

To send any kind of requests to the B2STAGE HTTP-API an authentication token is needed:

1. to request an authentication token the B2ACCESS credentials has to be sent in the request as shown in [B2ACCESS Authorization](#b2access-authorization). If the request succeeds, the server returns an authentication token;

2. once you obtain a valid authentication token user can send HTTP requests including the token in the "Authorization: Bearer" header (see [Send API request](#send-api-request)). Continue to send API requests with that token until the service completes the request or the Unauthorized (401) error occurs.

3. if the Unauthorized (401) error occurs, request another token (see point 1).


## B2ACCESS Authorization 

Credentials are a combination of your user name and password: they are needed to generate authentication tokens.

To allow the B2STAGE HTTP-API to access B2ACCESS user's account:

1. visit the following URL via a web browser:

```bash
http://<http_server:port>/auth/askauth
```

You will be redirect to the B2ACCESS log in page.

2. Log in using your EUDAT credentials. You will be redirect to a web page where you are prompted to authorize the B2STAGE HTTP-API to access some user profile information.

3. Click on "Confirm" to authorize the the B2STAGE HTTP-API.

4. You will be redirect to a page containing the auth-toekn to be used for each HTTP request (see [Send API request](#send-api-request)).

This is a one-time operation, needed only the first time you need to get access to the B2STAGE HTTP-API.


## Send API request
This section shows how to make a basic API call. For a complete list of API calls, see the [User documentation](user.md).

Every API request must contain a valid authentication token obtained using the Login API.
An example of API request is the following: 

```bash
$ curl http://<http_server:port>/api/status -H "Authorization: Bearer <auth_token>"
```
