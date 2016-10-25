
# Registered resources

The Pilot Release will focus on registered domain: the registered domain will include only registered entities (with a PID associated).
The endpoint URI will use the directory namespace.
Examples of endpoint URI are the following:

```bash
GET https://be2safexx.eudat.eu/api/registered/path/to/directory/filename
# will return a JSON containing the file metadata

GET https://be2safexx.eudat.eu/api/registered/path/to/directory/filename?download
# will download the file: "path/to/directory/filename"

GET https://be2safexx.eudat.eu/api/registered/path/to/directory
# will return a JSON containing the list of objects

---

POST file@myfile https://be2safexx.eudat.eu/api/registered?path=/path/to/directory/filename
# will upload "myfile" as "/path/to/directory/filename"
# and will trigger the registration in b2safe (IMPORTANT!)

---

PUT file@myfile https://be2safexx.eudat.eu/api/registered/path/to/directory/filename
# will upload "myfile" as "/path/to/directory/filename"
# and will trigger the registration in b2safe (IMPORTANT!)

PUT https://be2safexx.eudat.eu/api/registered/path/to/directory
# will create the directory "/path/to/directory" in b2safe

---

DELETE https://be2safexx.eudat.eu/api/registered/path/to/directory/filename
# will delete the file "/path/to/directory/filename"

DELETE https://be2safexx.eudat.eu/api/registered/path/to/directory
# will delete the directory "/path/to/directory" only if empty

---

PATCH https://be2safexx.eudat.eu/api/registered/path/to/directory/filename?newname=filename2
# will change the file name "path/to/directory/filename" to "path/to/directory/filename2"

PATCH https://be2safexx.eudat.eu/api/registered/path/to/directory?newname=directory2
# will change the directory name "path/to/directory" to "path/to/directory2"
```

