
# 1.0.3

todos

- elastic logs: CDI-%{+YYYY.MM.dd}
    + rabbit users: create + IPs
- workers try/catch (and send notification to MARIS) 
    + Irule failed: EXEC_CMD_ERROR
    + 54 "Internal error, restart your request"
- rocket chat backup to nfs dir
- test download iticket wrong code
- orders adding to zip
- list errors in steps for Maris to define codes @TODO
- rapydo stack command
    + rabbit
    + redis
    + elastic
    + logstash
- ansible the infrastructure
- auth forbidden to all for maris/admin only endpoint...
- cleaning
    + containers
    + batch moved into production
    + orders
- Log username sent from import manager
- Celery Prefetch Limits

## general

- `rapydo verify` all/single connection parameters
- docs on cron to create the certificate every 2 months
- dockerized Handle? https://hub.docker.com/r/osul/handle/

## seadata

### restricted orders

1. Restricted separated api call `PATCH`
2. Restricted and unrestricted zips separated
3. specify registered/unregistered when asking for a download @parameter


### snippets

1. Recover the PIDs from data in a folder in production

```python
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

2. Debug celery on ipython

```python
from restapi.flask_ext.flask_celery import CeleryExt
from restapi.flask_ext import get_debug_instance
obj = get_debug_instance(CeleryExt)
workers = obj.control.inspect()
workers.active()
```

3. Count current tasks in the queue

```bash
outfile="output.json"
TOKEN=$(http POST https://seadata.cineca.it/auth/b2safeproxy \
    username= password \
    | jq .Response.data.token -M -c -r)

http GET https://seadata.cineca.it/api/queue \
    Authorization:"Bearer $TOKEN" > $outfile

jq .Response.data output.json | grep status | wc -l
```

4. Add nfs client

```
apt-get install -y nfs-common
mkdir -p /nfs/share
130.186.13.150:/var/nfs/general /nfs/share nfs auto,nofail,noatime,nolock,intr,tcp,actimeo=1800 0 0
mount -a
```


--- 

ips: [
    "77.87.163.227", "77.87.163.244", "77.87.163.245", 
    "83.163.127.252", "80.127.238.100", "62.251.62.40", "80.101.105.184"
]
