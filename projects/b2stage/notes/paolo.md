
# 1.0.3

todos

## general

- `rapydo verify` all/single connection parameters
- docs on cron to create the certificate every 2 months
- dockerized Handle? https://hub.docker.com/r/osul/handle/

## seadata

### orders

1. Restricted separated api call `PATCH`
2. Restricted and unrestricted zips separated
3. specify registered/unregistered when asking for a download @parameter

### still missing

- ansible the infrastructure
- list errors in steps for Maris to define codes @TODO
- rabbitmq closed connection @TOFIX
- auth forbidden to all for maris/admin only endpoint

```
apt-get install -y nfs-common
mkdir -p /nfs/share
130.186.13.150:/var/nfs/general /nfs/share nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0
mount -a
```

### inefficiency

- Async ops @celery
- HTTP API logging: elastisearch (direct?)
- containers cleaning

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
