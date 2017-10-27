
# B2STAGE HTTP-API User Documentation

This guide describes the B2STAGE HTTP-API operations, related request, response structures and error codes.

The current release of the B2STAGE HTTP-API allows users to perform the following operations on B2SAFE:
- uploading an object on B2SAFE obtaining the checksum and the EUDAT PID;
- downloading an object from B2SAFE either passing the B2SAFE path or EUDAT PID;
- listing, renaming and deleting objects on B2SAFE;
- resolve EUDAT PIDS getting URL and EUDAT/CHECKSUM.

The complete description of the operation you can perform is available in:
- the [registered api](registered.md) page
- the [pids api](pids.md) page
- the [publish api](publish.md) page


## Authentication flow
The HTTP-API supports two kinds of authentication:
- via the B2ACCESS service (Oauth2 protocol + proxy certificates);
- via local B2SAFE credentials (username and password).

To send any kind of requests to the B2STAGE HTTP-API an authentication token is needed: 

1. the user requests an authentication token following the steps described in the [B2ACCESS](authentication.md) or in the [local B2SAFE credentials](authentication_b2safe.md) documentation pages. If the request succeeds, the server returns an authentication token;

2. once obtained a valid authentication token, the user can send HTTP requests to the B2STAGE http server including the token in the "Authorization: Bearer" header (see [Send API request](#send-api-request-example)).




## Send API request example
An example of API request is the following: 
```bash
$ curl \
  -H "Authorization: Bearer <auth_token>" \
  <http_server:port>/api/status 
```

>Note: According to the EUDAT Data Architecture B2SAFE is part of the registered data domain, where digital objects are stored and managed in such a way that data carrying associated descriptive metadata is discoverable and can be referred to or retrieved using persistent identifiers.