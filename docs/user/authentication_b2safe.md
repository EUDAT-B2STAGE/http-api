# Authentication with B2SAFE credentials

The B2STAGE HTTP-API supports authentiction using local B2SAFE credentials (username and password).

Therefore, to use the B2STAGE HTTP-API service, you need a B2SAFE user on the B2SAFE instance which the HTTP-API is connected to. Please refer to the B2SAFE service if you need one.

To obatin an access token using local B2SAFE credentilas the following enpoint is available:

- /auth/b2safeproxy - *request an access token*


## **GET**
### Obtain an access token
##### Example
```bash
$ curl <http_server:port>/auth/b2safeproxy -d "username=<b2safe_username>&password=<b2safe_password>"
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
      "b2safe_home": "/path/to/home", 
      "b2safe_user": "<b2safe_username>", 
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTcwM2MwN2EtOTlkNC00YWVmLWE0MDQtNTlhN2ZiYjhmYWRmIiwianRpIjoiYWIyNmU5NmQtZDMyYy00MDM4LWIyYTEtNzQ4ODE4NDljOTBkIn0.3z54pB8OqonEIwQN8ioPcN4P6F7Ga0WW-2gBZjuSIl0"
    }, 
    "errors": null
  }
}

```
The token received (in our example:
"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiOTcwM2MwN2EtOTlkNC00YWVmLWE0MDQtNTlhN2ZiYjhmYWRmIiwianRpIjoiYWIyNmU5NmQtZDMyYy00MDM4LWIyYTEtNzQ4ODE4NDljOTBkIn0.3z54pB8OqonEIwQN8ioPcN4P6F7Ga0WW-2gBZjuSIl0Y") must be used in each HTTP request