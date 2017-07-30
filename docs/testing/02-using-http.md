# Using the HTTP API

You can retrieve information on the API either via exploring it with Swagger (See Section ??) or via the endpoint

```
http://<fqdn>:8080/api/specs
```

## cURL
It is is wise to store some recurring parameters in shell variables:

```sh
export SERVER="<FQDN>"
export PORT="8080"
export IHOME="/tempZone/home/guest" #iRODS home collection for the test user
```

For the develop instance you will use simple username password authentication.
Obtain a token from the HTTP API

```sh
curl -X POST http://$SERVER:$PORT/auth/login -d \
'{"username":"user@nomail.org","password":"test"}'

{
    "Meta": {
        "data_type": "<class 'dict'>",
        "elements": 1,
        "errors": 0,
        "status": 200
    },
    "Response": {
        "data": {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9 ... "
        },
        "errors": null
    }
}
```

The token can be used to issues requests to the HTTP API. Note that the token is just valid for a certain time. _**Todo: find out for how long.**_

Now you can ask the HTTP API which priviledges you have

```sh
export TOKEN='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9 ...'

curl -X GET --header "Authorization: Bearer $TOKEN" "http://$SERVER:$PORT/api/admin"

{
  "Meta": {
    "data_type": "<class 'str'>",
    "elements": 1,
    "errors": 0,
    "status": 200
  },
  "Response": {
    "data": "I am admin!",
    "errors": null
  }
}
```
**NOTE**: The call returns you your role in the HTTP API not in the iRODS instance!

## Listing

```sh
curl -H "Authorization: Bearer $TOKEN" \
	http://$SERVER:$PORT/api/registered$IHOME
```
At the beginning the iRODS collection is empty.

## Put data

```sh
curl -X PUT -H "Authorization: Bearer $TOKEN" -F file=@test.txt \
	http://$SERVER:$PORT/api/registered$IHOME/test.txt
```

Check with 

```sh
curl -H "Authorization: Bearer $TOKEN" \
	http://$SERVER:$PORT/api/registered$IHOME
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
        "test.txt": {
          "dataobject": "test.txt",
          "link": "http://localhost/api/registered/tempZone/home/guest/test.txt",
          "location": "irods://rodserver.dockerized.io/tempZone/home/guest",
          "metadata": {
            "EUDAT/FIO": null,
            "EUDAT/FIXED_CONTENT": null,
            "EUDAT/PARENT": null,
            "EUDAT/REPLICA": null,
            "EUDAT/ROR": null,
            "PID": null,
            "checksum": null,
            "name": "test.txt",
            "object_type": "dataobject"
          },
          "path": "/tempZone/home/guest"
        }
      }
    ],
    "errors": null
  }
}
```

## Create collections: the *b2safe* collection
To trigger the B2SAFE event hook, we need a collection *b2safe*

```sh
curl -X POST \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-d '{"path":"/tempZone/home/guest/b2safe"}' \
http://$SERVER:$PORT/api/registered
```

Now upload data to the archive collection:

```sh
curl -X PUT -H "Authorization: Bearer $TOKEN" \
-F file=@test.txt \ 
http://$SERVER:$PORT/api/registered$IHOME/b2safe/test.txt
```
This command can take some time, snice it triggers the B2SAFE replication.

Let us check what happened to the *b2safe* collection:

```sh
curl -H "Authorization: Bearer $TOKEN" \
	http://$SERVER:$PORT/api/registered$IHOME/b2safe/
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
        "test.txt": {
          "dataobject": "test.txt",
          "link": "http://localhost/api/registered/tempZone/home/guest/archive/test.txt",
          "location": "irods://rodserver.dockerized.io/tempZone/home/guest/archive",
          "metadata": {
            "EUDAT/FIO": null,
            "EUDAT/FIXED_CONTENT": "False",
            "EUDAT/PARENT": null,
            "EUDAT/REPLICA": "21.T12995/5b2923ba-6d51-11e7-b75c-0242ac010003",
            "EUDAT/ROR": null,
            "PID": "21.T12995/5a639b68-6d51-11e7-a170-0242ac010003",
            "checksum": "sha2:FRIaSMWVYLAGFlMjEQEQibjdMu70Ki5usj+SHpaPAsg=",
            "name": "test.txt",
            "object_type": "dataobject"
          },
          "path": "/tempZone/home/guest/archive"
        }
      }
    ],
    "errors": null
  }
}
```

And the replication collection:

```sh
curl -H "Authorization: Bearer $TOKEN" \
	http://$SERVER:$PORT/api/registered$IHOME/b2replication
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
        "test.txt": {
          "dataobject": "test.txt",
          "link": "http://localhost/api/registered/tempZone/home/guest/b2replication/test.txt",
          "location": "irods://rodserver.dockerized.io/tempZone/home/guest/b2replication",
          "metadata": {
            "EUDAT/FIO": "21.T12995/5a639b68-6d51-11e7-a170-0242ac010003",
            "EUDAT/FIXED_CONTENT": "False",
            "EUDAT/PARENT": "21.T12995/5a639b68-6d51-11e7-a170-0242ac010003",
            "EUDAT/REPLICA": null,
            "EUDAT/ROR": "21.T12995/5a639b68-6d51-11e7-a170-0242ac010003",
            "PID": "21.T12995/5b2923ba-6d51-11e7-b75c-0242ac010003",
            "checksum": "sha2:FRIaSMWVYLAGFlMjEQEQibjdMu70Ki5usj+SHpaPAsg=",
            "name": "test.txt",
            "object_type": "dataobject"
          },
          "path": "/tempZone/home/guest/b2replication"
        }
      }
    ],
    "errors": null
  }
}
```

**Note**: The collections _archive_ and _replication_ did not receive a PID.





