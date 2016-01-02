
# Manage APIs

## Add an endpoint: quick way (**NOT** recommended)

Edit `restapi/resources/exampleservices.py` and add a rest class:

* The class must extend `ExtendedApiResource`
* The class should use the decorator `@for_all_api_methods(standardata)`
* Provide at least the `get` method

The base code is found inside the `restapi.resources.base` module. Please check the provided examples inside the module to write the right code.

**Test it**: if your class is called `MyClass`, it will be reachable at the address `http://HOST:PORT/api/myclass` address of the running server.
You can also specify a different address, by overiding the attribute `endpoint` of your class.

## Add an endpoint: a better option (*recommended*)

The protocol requires three steps.

* **STEP 1**: Create a resourse file with your endpoints.

To get started you may copy
[the example](https://github.com/pdonorio/rest-mock/blob/master/restapi/resources/exampleservices.py). Your resourse file has to be placed in the [resource directory](https://github.com/pdonorio/rest-mock/tree/master/restapi/resources)

* **STEP 2**: Define a file `confs/endpoints.ini` with the following syntax:

```
[module_name]
class=endpoint
```

For example, after creating a file `myresource.py` inside `restapi/resources`,
containing two classes `One` and `Two`, you could use:

```
[myresource]
One=foo
Two=hello/world
```

The system would provide the two following working URLs:

```
# Resource One
http://localhost:8081/api/foo
# Resource Two
http://localhost:8081/api/hello/world
```

* **STEP 3**: test your endpoints URL by running a server.

```bash
curl http://localhost:8081/api/foo
```

Also as provided example of using a key with an endpoint
but getting a (programmatic) error response, you may test:
```
curl -v http://localhost:8081/api/hello/world/keyword
```

<small> Note: `localhost:8081` should change to your server ip and port.
The above example is based on running docker compose on linux.</small>

## Make classes and methods your endpoints

You either have to ways of making endpoints, as you may see in the example:

1) Add a decorator to a method of a class:

```python
from .. import get_logger
from .base import ExtendedApiResource
from . import decorators as decorate

class MyAPI(ExtendedApiResource):

    # Only this method of my class is an endpoint
    @decorate.apimethod
    def get(self):
        return "I am a REST API endpoint for method GET"
```

2) Add a decorator to the whole class

```python
@decorate.enable_endpoint_identifier('myid')
class MyAPI(ExtendedApiResource):

    def get(self, myid=None):
        if myid is not None:
            logger.debug("Received request for id '%s'" % myid )
        return "I am a REST API endpoint for method GET"

    def post(self, myid=None):
        if myid is not None:
            logger.debug("Received request for id '%s'" % myid )
        return "I am a REST API endpoint for method POST"
```

Then test your resources on both get or post:

```bash
http GET http://localhost:8081/api/myapi
http GET http://localhost:8081/api/myapi/42
http POST http://localhost:8081/api/myapi
http POST http://localhost:8081/api/myapi/28
```

Note: decorators search only for 'get', 'post', 'put' and 'delete' REST methods.

## Securing endpoints

To let only logged user which provide a valid token, access your endpoint,
you need the `auth_token_required` decorator:

```python
from flask.ext.security import auth_token_required

@decorate.apimethod
@auth_token_required
def get(self):
    return "Only if logged"
```

To specify which roles are needed (one or more), there is another decorator called
`roles_required`:

```python
from flask.ext.security import roles_required, auth_token_required
from confs import config

@decorate.apimethod
@auth_token_required
@roles_required(config.ROLE_ADMIN)
def get(self):
    return "Only if admin"
```

You can define more roles inside `confs/config.py`.

For more information about security works and how to get a token,
please [read the proper section](security.md).
