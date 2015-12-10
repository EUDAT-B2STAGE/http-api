
# API

This part covers the backend configuration.

## Add resources as REST API endpoints

Edit the file `vanilla/specs/endpoints.ini`, using the following syntax:

```
[custom.my_module_name]
MyClass=endpoint/path
```

All APIs will be reachable with the FIXED prefix `HOST:PORT/api/yourendpoint`
