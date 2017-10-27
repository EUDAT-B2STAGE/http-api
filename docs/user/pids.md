# Pids APIs

The pids APIs allow the resolution of public EUDAT PIDS, getting the URL of the digital object identified by the PID.
It is also possible to download the file which the PID points to: this is can be performed only if the returned URL is managable by the current HTTP-API server 
(i.e the returned URL fromt he PID resolution is equal to the HTTP-API server host URL).
<!-- maybe we nedd an example to make this clearer -->

The examples in this section use cURL commands. For information about cURL, see http://curl.haxx.se/.


## Methods
1. [GET](#get)

---

## **GET**

### Resolve PID

##### Example

```bash
# Resolve <PID> (e.g. 11100/33ac01fc-6850-11e5-b66e-e41f13eb32b2)
$ curl \
  -H "Authorization: Bearer <auth_token>"  \
  <http_server:port>/api/pids/<PID> 
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
            "EUDAT/CHECKSUM": '123456789',
            "URL": "<http_server:port>/api/registered/tempZone/home/guest/test.txt"
        },
        "errors": null
    }
}
```


### Resolve PID and download object

##### Example

```bash
# Get 'filename.txt' metadata
$ curl \
  -H "Authorization: Bearer <auth_token>"  \
  <http_server:port>/api/pids/<PID>?download=true
```

##### Response

```json
Content of the object to which the PID points to (if reachable by the HTTP-API server)
```