
## notes

**PRIORITIES** ::MVP::

* credentials
* list the zip files
* unwanted characters in filenames (ONLY CHECK)
* HTTP API logging into elastisearch
* push 1 thousand files in production from RAR
- Restricted data prototype
- Log username sent from import manager
- more than one zip file in one unrestricted order

---

- cron to create the certificate every 80 days
- dockerized Handle? https://hub.docker.com/r/osul/handle/

---

Missing:
- async with celery
- auth forbidden for maris only endpoint
- how to give back errors correctly to Import Manager
- guys in hometown to discuss the Python code
- ansible the infrastructure
- rocket chat to CSC

---

```python
""" Recover the PIDs from data in a folder in production """
mypath = '/bla/bla'
imain = self.get_service_instance(service_name='irods')
files = imain.list(mypath)
from utilities import path

kv = {}
for element in files:
    ipath = path.join(mypath, element, return_str=True)
    metadata, _ = imain.get_metadata(ipath)
    # log.pp(metadata)
    kv[element] = metadata.get('PID')
    # break
# log.pp(kv)
return kv
```
