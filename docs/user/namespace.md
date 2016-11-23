
# Namespace APIs

>Note: According to the EUDAT Data Architecture B2SAFE is part of the registered data domain, where digital objects are stored and managed in such a way that data carrying associated descriptive metadata is discoverable and can be referred to or retrieved using persistent identifiers.
>For the time being B2SAFE object registration policies are not applied to a specific path, but can be configured to trigger the registration in any available paths. Therefore the B2STAGE HTTP-API can not guarantee that an uploaded file will be registered by B2SAFE.
>Until this behaviour is in place, we are not using **registered** in the endpoint URL, but **namespace**. As B2SAFE is fully complaint to the EUDAT Data Architecture, *namespace* will replaced by *registered*: please consider it as a temporary placeholder.

The namespace APIs allow the management of entities on B2SAFE.
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
### Obtain entity metadata
##### Example
```bash
# Get 'filename.txt' metadata
$ curl https://<http_server:port>/api/namespace/path/to/directory/filename.txt -H "Authorization: Bearer <auth_token>"
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
      [
        "data_name", 
        "filename.txt"
      ]
    ], 
    "errors": null
  }
}

```

### Download an entity
##### Example
```bash
# Download 'filename.txt'
$ curl https://<http_server:port>/api/namespace/path/to/directory/filename.txt?download=true -H "Authorization: Bearer <auth_token>"
```
##### Response
```json
Content of filename.txt
```

### Get list of entities in a directory
##### Example
```bash
# Get list of entities inside 'directory'
$ curl https://<http_server:port>/api/namespace/path/to/directory/ -H "Authorization: Bearer <auth_token>"
```
##### Response
```json
{
  "Meta": {
    "data_type": "<class 'dict'>", 
    "elements": 2, 
    "errors": 0, 
    "status": 200
  }, 
  "Response": {
    "data": {
      "myfile.txt": {
        "acl": null, 
        "acl_inheritance": null, 
        "content_length": "4248", 
        "last_modified": "2016-11-23.15:23", 
        "name": "myfile.txt", 
        "object_type": "dataobject", 
        "owner": "username", 
        "path": ""
      }, 
      "myfile2.txt": {
        "acl": null, 
        "acl_inheritance": null, 
        "content_length": "2617", 
        "last_modified": "2016-11-23.15:12", 
        "name": "myfile2.txt", 
        "object_type": "dataobject", 
        "owner": "username", 
        "path": ""
      }
    }, 
    "errors": null
  }
}
```


## **PUT**
### Upload an entity **and trigger the registration in B2SAFE**

> Notes: The entity registration depends on the policies adopted by the B2SAFE instance which the B2STAGE HTTP-API is connected to. This operation is idempotent.

##### Parameters
| Parameter | Type | Description
|-----------|------|-------------
| file (required) | string | Name of the local file to be uploaded
| force | bool | Force overwrite

##### Examples
```bash
# create 'myfile.txt' as '/path/to/directory/filename'
$ curl -X PUT -F file=@myfile.txt  https://<http_server:port>/api/namespace/path/to/directory/filename -H "Authorization: Bearer <auth_token>"

# overwrite 'myfile2.txt' as '/path/to/directory/filename'
$ curl -X PUT -F file=@myfile2.txt  https://<http_server:port>/api/namespace/path/to/directory/filename?force=true -H "Authorization: Bearer <auth_token>"
```
##### Response
```json
{
  "Meta": {
    "data_type": "<class 'dict'>", 
    "elements": 5, 
    "errors": 0, 
    "status": 200
  }, 
  "Response": {
    "data": {
      "filename": "myfile", 
      "link": "http://172.17.0.4:5000/api/namespace/path/to/directory/myfile.txt", 
      "location": "irods:///b2safe.cineca.it/path/to/directory/myfile.txt", 
      "path": "/path/to/directory/myfile.txt", 
      "resources": [
        "myResc"
      ]
    }, 
    "errors": null
  }
}
```

---

## **POST**
### Create a new directory
| Parameter | Type | Description
|-----------|------|-------------
| path (required) | string | Absolute directory path to be created 
| force | bool | Force recursive creation

##### Example
```bash
# Create the directory '/new_directory' in B2SAFE
$ curl -X POST -d path=/path/to/directory/new_directory/ https://<http_server:port>/api/namespace -H "Authorization: Bearer <auth_token>"
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
      "link": "http://<http_server:port>/api/namespace/path/to/directory/new_directory", 
      "location": "irods:///b2safe.cineca.it/path/to/directory/new_directory", 
      "path": "/path/to/directory/new_directory"
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
$ curl -X DELETE https://<http_server:port>/api/namespace/path/to/directory/file.txt -H "Authorization: Bearer <auth_token>"
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
      "requested removal": "/path/to/directory/file.txt"
    }, 
    "errors": null
  }
}

```

### Delete an empty directory

##### Example
```bash
# Delete "directory" (only if empty)
$ curl -X DELETE https://<http_server:port>/api/namespace/path/to/directory/ -H "Authorization: Bearer <auth_token>"
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
      "requested removal": "/path/to/directory/"
    }, 
    "errors": null
  }
}
```

---

## **PATCH**
### Update an entity name
##### Parameters
| Parameter | Type | Description
|-----------|------|-------------
| newname | string | Name that will replace the old one

##### Example
```bash
PATCH -d newname=filename2 https://<http_server:port>/api/registered/path/to/directory/filename
# change the file name "path/to/directory/filename" to "path/to/directory/filename2"
```
##### Response
```json
[JSON example]
```

### Update a directory name
##### Parameters
| Parameter | Type | Description
|-----------|------|-------------
| newname | string | Name that will replace the old one

##### Example
```bash
PATCH -d newname=directory2 https://<http_server:port>/api/registered/path/to/directory
# change the directory name "path/to/directory" to "path/to/directory2"
```
##### Response
```json
[JSON example]
```
