
# Registered APIs


The registered APIs allow to managed registerd registered entities (entitied with a PID associated).
The endpoint URI will use the directory namespace.
The examples in this section use cURL commands. For information about cURL, see http://curl.haxx.se/.

## Methods
1. [GET](#get)
2. [POST](#post)
3. [PUT](#put)
4. [DELETE](#delete)
5. [PATCH](#patch)

---
# GET

### Obtain entity metadata
##### Example
```bash
GET https://be2safexx.eudat.eu/api/registered/path/to/directory/filename
# return a JSON containing the 'filename' metadata
```
##### Response
[JSON example]


#### Download entity
##### Example
```bash
GET https://be2safexx.eudat.eu/api/registered/path/to/directory/filename?download
# download 'filename'
```
##### Response
[JSON example]


### Get list of entities in a collection
##### Example
```bash
GET https://be2safexx.eudat.eu/api/registered/path/to/directory
# return a JSON containing the list of entities inside 'directory'
```
##### Response
[JSON example]

---
# POST

### Upload an entity and trigger the registration in b2safe (IMPORTANT!)

##### Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| file  | string | Name of the local file to be uploaded  |
| path  | string | The path in which you wanto to upload the entity (home is the default)  |


##### Example
```bash
POST file@myfile https://be2safexx.eudat.eu/api/registered?path=/path/to/directory/filename
# upload 'myfile' as '/path/to/directory/filename' and trigger the registration in B2SAFE
```

##### Response
[JSON example]

---
# PUT

### Upload an entity *and trigger the registration in B2SAFE*

##### Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| file | string | Name of the local file to be uploaded  |

##### Example
```bash
PUT file@myfile https://be2safexx.eudat.eu/api/registered/path/to/directory/filename
# upload 'myfile' as '/path/to/directory/filename' and trigger the registration in B2SAFE
```

##### Response
[JSON example]


### Create a new direcoty

##### Example
```bash
PUT https://be2safexx.eudat.eu/api/registered/path/to/directory
# create the directory '/path/to/directory' in B2SAFE
```

##### Response
[JSON example]

---
# DELETE

### Delete an entity 

##### Example
```bash
DELETE https://be2safexx.eudat.eu/api/registered/path/to/directory/filename
# delete the file '/path/to/directory/filename'
```

##### Response
[JSON example]


### Delete a directory 

##### Example
```bash
DELETE https://be2safexx.eudat.eu/api/registered/path/to/directory
# delete the directory "/path/to/directory" only if empty
```

##### Response
[JSON example]

---
# PATCH

### Update an entity name

##### Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| newname | string | Name that will replace the old one  |

##### Example
```bash
PATCH https://be2safexx.eudat.eu/api/registered/path/to/directory/filename?newname=filename2
# change the file name "path/to/directory/filename" to "path/to/directory/filename2"
```

##### Response
[JSON example]


### Update a directory name

##### Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| newname | string | Name that will replace the old one  |

##### Example
```bash
PATCH https://be2safexx.eudat.eu/api/registered/path/to/directory?newname=directory2
# change the directory name "path/to/directory" to "path/to/directory2"
```

##### Response
[JSON example]

