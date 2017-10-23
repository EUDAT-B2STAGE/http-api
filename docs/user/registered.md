
# Registered APIs

>Note: According to the EUDAT Data Architecture B2SAFE is part of the registered data domain, where digital objects are stored and managed in such a way that data carrying associated descriptive metadata is discoverable and can be referred to or retrieved using persistent identifiers.
>For the time being B2SAFE object registration policies are not applied to a specific path, but can be configured to trigger the registration in any available paths. Therefore the B2STAGE HTTP-API can not guarantee that an uploaded file will be registered by B2SAFE.

The registered APIs allow the management of entities on B2SAFE.
The following operations are currently available:
- list, upload, download and delete files (objects in iRODS) 
- create and delete directories (collection in iRODS).

The endpoint methods will use the directory namespace (iRODS full path) to identify entities .
The examples in this section use cURL commands. For information about cURL, see http://curl.haxx.se/.


## Methods
1. [GET](#get)
2. [PUT](#put)
3. [POST](#post)
4. [DELETE](#delete)
5. [PATCH](#patch)

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

Both Form and Streaming upload are supported. Streaming is faster and does load the file in memory on client side.

> Notes: The entity registration depends on the policies adopted by the B2SAFE instance which the B2STAGE HTTP-API is connected to. This operation is idempotent.

##### Parameters
| Parameter | Type | Description
|-----------|------|-------------
| file (required) | string | Name of the local file to be uploaded
| force | bool | Force overwrite
| pid_await | bool | Return PID (synchronous)

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

---
## **DELETE**
### Delete an entity

##### Example
```bash
# Delete the file '/path/to/directory/file.txt'
$ curl -X DELETE \
  -H "Authorization: Bearer <auth_token>" \
  <http_server:port>/api/registered/path/to/directory/file.txt 
```
##### Response
```json
{
  "Meta": {
    "data_type": "<class 'dict'>", 
    "elements": 1, 
    "errors": 0, 
    "status": 200
  }, 
  "Response": {
    "data": {
      "removed": "/path/to/directory/file.txt"
    }, 
    "errors": null
  }
}

```

### Delete an empty directory

##### Example
```bash
# Delete "directory" (only if empty)
$ curl -X DELETE \
  -H "Authorization: Bearer <auth_token>" \
  <http_server:port>/api/registered/path/to/directory/ 
```
##### Response
```json
{
  "Meta": {
    "data_type": "<class 'dict'>", 
    "elements": 1, 
    "errors": 0, 
    "status": 200
  }, 
  "Response": {
    "data": {
      "removed": "/path/to/directory/"
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
