
# Registered APIs

> NOTE: The endpoint called *registered* corresponds to a domain in iRODS, where each data object carries a persistent identifier (PID). The HTTP API itself does **not** assign the PID, this is done by iRODS rules, e.g. eventhooks in iRODS calliong the B2SAFE PID registration rule.

> By default, when you enabled your iRODS instance with the HTTP API but did not install B2SAFE or configured these eventhooks **no PIDs will be assigned**.

> For the time being B2SAFE object registration policies are not applied to a specific path, but can be configured to trigger the registration in any available paths. Therefore the B2STAGE HTTP-API can not guarantee that an uploaded file will be registered by B2SAFE.

The registered APIs allow the management of entities on B2SAFE.
The following operations are currently available:
- list, upload, download and rename files (objects in iRODS) 
- create and rename directories (collection in iRODS).

The endpoint methods will use the directory namespace (iRODS full path) to identify entities .
The examples in this section use cURL commands. For information about cURL, see http://curl.haxx.se/.


## Methods

* [GET](#get)
* [PUT](#put)
* [POST](#post)
* [PATCH](#patch)

> note: the `DELETE` action is **NOT** allowed in the *"registered" domain*.

---

## **GET**
### Obtain entity metadata (with PID, if available)
##### Example
```bash
# Get 'filename.txt' metadata
$ curl \
  -H "Authorization: Bearer <auth_token>"  \
  <http_server:port>/api/registered/path/to/directory/filename.txt 
```
##### Response
```json
{
    "Meta": {
        "data_type": "<class 'list'>",
        "elements": 1,
        "errors": 0,
        "status": 200
    },
    "Response": {
        "data": [
            {
                "filename.txt": {
                    "dataobject": "filename.txt",
                    "link": "<http_server:port>/api/registered/path/to/directory/filename.txt",
                    "location": "irods://rodserver.dockerized.io/path/to/directory/filename.txt",
                    "metadata": {
                        "PID": '123/1234567890',
                        "checksum": '123456789',
                        "name": "filename.txt",
                        "object_type": "dataobject"
                    },
                    "path": "path/to/directory"
                }
            }
        ],
        "errors": null
    }
}


```

### Download an entity
##### Example
```bash
# Download 'filename.txt'
$ curl -o localFileName \
  -H "Authorization: Bearer <auth_token>" \
  <http_server:port>/api/registered/path/to/directory/filename.txt?download=true 
```
##### Response
```json
Content of filename.txt
```

### Get list of entities in a directory
##### Example
```bash
# Get list of entities inside 'directory'
$ curl \
  -H "Authorization: Bearer <auth_token>" \
  <http_server:port>/api/registered/path/to/directory/ 
```
##### Response
```json
{
  "Meta": {
    "data_type": "<class 'list'>", 
    "elements": 2, 
    "errors": 0, 
    "status": 200
  }, 
  "Response": {
    "data": [
      {
        "filename.txt": {
          "dataobject": "filename.txt", 
          "link": "<http_server:port>/api/registered/path/to/directory/filename.txt", 
          "location": "irods://rodserver.dockerized.io/path/to/directory/", 
          "metadata": {
            "PID": "123/1234567890", 
            "checksum": "1234567890", 
            "name": "filename.txt", 
            "object_type": "dataobject"
          }, 
          "path": "/path/to/directory"
        }
      }, 
      {
        "test": {
          "dataobject": "test", 
          "link": "<http_server:port>/api/registered/path/to/directory/test", 
          "location": "irods://rodserver.dockerized.io/path/to/directory", 
          "metadata": {
            "PID": null, 
            "checksum": "9876543210",
            "name": "test", 
            "object_type": "dataobject"
          }, 
          "path": "/path/to/directory"
        }
      }
    ], 
    "errors": null
  }
}

```


## **PUT**
### Upload an entity **and trigger the registration in B2SAFE**

Both Form and Streaming upload are supported. Streaming is more advisable uploding large data. Also be aware that for larger and longer upload you might have to provide a bigger timeout parameter to your client if any (e.g. for `curl` there is a `--max-time` option)

> Notes: The entity registration depends on the policies adopted by the B2SAFE instance which the B2STAGE HTTP-API is connected to. This operation is idempotent.

##### Parameters

| Parameter | Type | Description
|-----------|------|-------------
| file (required) | string | Name of the local file to be uploaded
| force | bool | Force overwrite
| pid_await | bool | Return PID in the response: the response is returned as the registration is completed (or after 10 seconds if the PID is not ready yet)

##### Example: Form upload
```bash
# Form upload 'myfile' in '/path/to/directory/filename'
$ curl -X PUT \
  -H "Authorization: Bearer <auth_token>"
  -F file=@myfile \
  <http_server:port>/api/registered/path/to/directory/filename

# Overwrite 'myfile2' as '/path/to/directory/filename'
$ curl -X PUT \
  -H "Authorization: Bearer <auth_token>" \
  -F file=@myfile2 \
  <http_server:port>/api/registered/path/to/directory/filename?force=true 

# Form upload 'myfile' and get the PID in the response
$ curl -X PUT \
  -H "Authorization: Bearer <auth_token>" \
  -F file=@myfile2 \
  <http_server:port>/api/registered/path/to/directory/filename?pid_await=true 
```
##### Example: Streaming upload
```bash
# Streaming upload 'myfile' in '/path/to/directory/filename'
$ curl -T file \
  -H "Authorization: Bearer <auth_token>"
  -H "Content-Type: application/octet-stream"
  <http_server:port>/api/registered/path/to/directory/filename
```
##### Example: Streaming upload with python requests
```python
# Streaming upload 'myfile' in '/path/to/directory/filename'
import requests

headers = {"Authorization":"Bearer <token>", "Content-Type":"application/octet-stream"}

with open('/tmp/file', 'rb') as f:
    requests.put('<http_server:port>/api/registered/path/to/directory/filename', data=f, headers=headers)
```

##### Response
```json
{
    "Meta": {
        "data_type": "<class 'dict'>",
        "elements": 6,
        "errors": 0,
        "status": 200
    },
    "Response": {
        "data": {
            "PID": null,
            "checksum": '123456789',
            "filename": "filename",
            "link": "<http_server:port>/api/registered/path/to/directory/filename",
            "location": "irods://rodserver.dockerized.io/path/to/directory/filename",
            "path": "/tempZone/home/guest"
        },
        "errors": null
    }
}

```


## **POST**
### Create a new directory
| Parameter | Type | Description
|-----------|------|-------------
| path (required) | string | Absolute directory path to be created 
<!-- | force | bool | Force recursive creation -->

##### Example
```bash
# Create the directory '/new_directory' in B2SAFE
$ curl -X POST \
  -H "Authorization: Bearer <auth_token>" \
  -H "Content-Type: application/json" \
  -d '{"path":"/path/to/directory/new_directory"}' \
  <http_server:port>/api/registered
```
##### Response
```json
{
  "Meta": {
    "data_type": "<class 'dict'>", 
    "elements": 3, 
    "errors": 0, 
    "status": 200
  }, 
  "Response": {
    "data": {
      "link": "<http_server:port>/api/registered/path/to/directory/new_directory", 
      "location": "irods://rodserver.dockerized.io/path/to/directory/new_directory", 
      "path": "/path/to/directory/new_directory
    }, 
    "errors": null
  }
}

```


## **PATCH**
### Update an entity name
##### Parameters
| Parameter | Type | Description
|-----------|------|-------------
| newname | string | Name that will replace the old one

##### Example
```bash
# Rename the file "path/to/directory/filename" in "path/to/directory/filename2"
curl -X PATCH \
  -H "Authorization: Bearer <auth_token>" \
  -d '{"newname":"filename4"}' \
  <http_server:port>/api/registered/path/to/directory/filename
```
##### Response
```json
{
  "Meta": {
    "data_type": "<class 'dict'>", 
    "elements": 4, 
    "errors": 0, 
    "status": 200
  }, 
  "Response": {
    "data": {
      "filename": "filename2", 
      "link": "<http_server:port>/api/registered/path/to/directory/filename2", 
      "location": "irods://b2safe.cineca.it/path/to/directory/filename2", 
      "path": "/path/to/directory"
    }, 
    "errors": null
  }
}
```

### Update a directory name
##### Parameters
| Parameter | Type | Description
|-----------|------|-------------
| newname | string | Name that will replace the old one

##### Example
```bash
# Rename the directory "path/to/directory" in "path/to/directory2"
curl -X PATCH \
  -H "Authorization: Bearer <auth_token>" \
  -d '{"newname":"directory2"}' \
  <http_server:port>/api/registered/path/to/directory
```
##### Response
```json
{
  "Meta": {
    "data_type": "<class 'dict'>", 
    "elements": 4, 
    "errors": 0, 
    "status": 200
  }, 
  "Response": {
    "data": {
      "filename": "test1", 
      "link": "<http_server:port>/api/registered/path/to/directory2", 
      "location": "irods://b2safe.cineca.it/path/to/directory2", 
      "path": "/path/to"
    }, 
    "errors": null
  }
}
```
