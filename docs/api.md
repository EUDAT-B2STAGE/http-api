
# API

This part covers the backend configuration.

## Add resources as REST API endpoints

**Step 1**:

Create your endpoint Python file, e.g. `vanilla/apis/myfile.py`.
There is already an example file you may copy or edit, called `vanilla/apis/foo.py`.

**Step 2**:

Edit the file `vanilla/specs/endpoints.ini`, using the following syntax:

```
[custom.my_module_name]
MyClass=endpoint/path
```

The `foo.py` class is already available as first example inside the initial `endpoints.ini` file.

All APIs will be reachable with the FIXED prefix `HOST:PORT/api/yourendpoint`
