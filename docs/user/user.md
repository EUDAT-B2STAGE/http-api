
# B2STAGE HTTP-API User Documentation

This guide describes the B2STAGE HTTP-API operations, related request and response structures, and error codes.

To send any kind of requests to the B2STAGE HTTP-API an *authentication token*is needed: vist this the [Authentication documentation](authentication.md) for further details.

The alpha release of the B2STAGE HTTP-API allows user to perform the following operations on B2SAFE:
- list, upload, download and delete files (objects in iRODS) 
- create and delete directories (collection in iRODS).

The complete description of the operation you can perform on B2SAFE is available in the [namespace api](registered.md) page.

>Note: According to the EUDAT Data Architecture B2SAFE is part of the registered data domain, where digital objects are stored and managed in such a way that data carrying associated descriptive metadata is discoverable and can be referred to or retrieved using persistent identifiers.
Since B2SAFE still manages also non registered entities, we are not using *registered* in the endpoint URL. As B2SAFE is fully complaint to the EUDAT Data Architecture, **namespace** will replaced by **registered**: please consider it as a temporary placeholder.

