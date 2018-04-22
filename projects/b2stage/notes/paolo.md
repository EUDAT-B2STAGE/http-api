
# 1.0.2

todos

## general

- cron to create the certificate every 80 days
- dockerized Handle? https://hub.docker.com/r/osul/handle/

## seadata

### inefficiency

- HTTP API logging into elastisearch (direct?)
- Async ops @celery
    + irods copy and PIDs #slow
    + approve: recover pids and send to maris
    + orders: create zip files 
        * restricted / unrestricted
- containers cleaning

### still missing

- ansible the infrastructure
- auth forbidden for maris only endpoint
- how to give back errors correctly to Import Manager

### notes

- rocket chat to somewhere else
- Restricted data prototype
    - restricted metadata on POST
    - restricted upload PUT + async container 
        + with curl call to Maris API
- Log username sent from import manager
- more than one zip file in one unrestricted order

### snippets

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
