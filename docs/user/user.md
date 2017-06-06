
# B2STAGE HTTP-API User Documentation

This guide describes the B2STAGE HTTP-API operations, related request, response structures and error codes.

The alpha release of the B2STAGE HTTP-API allows user to perform the following operations on B2SAFE:
- uploading an object on B2SAFE obtaining the checksum and the EUDAT PID;
- downloading an object from B2SAFE either passing the B2SAFE path or EUDAT PID;
- listing, renaming and deleting objects on B2SAFE;
- resolve EUDAT PIDS getting URL and EUDAT/CHECKSUM.

The complete description of the operation you can perform is available in:
- the [registered api](registered.md) page
- the [pids api](pids.md) page

To send any kind of requests to the B2STAGE HTTP-API an *authentication token* is needed: vist this the [Authentication documentation](authentication.md) for further details.

## Send API request example
An example of API request is the following: 
```bash
$ curl \
  -H "Authorization: Bearer <auth_token>" \
  <http_server:port>/api/status 
```

>Note: According to the EUDAT Data Architecture B2SAFE is part of the registered data domain, where digital objects are stored and managed in such a way that data carrying associated descriptive metadata is discoverable and can be referred to or retrieved using persistent identifiers.

