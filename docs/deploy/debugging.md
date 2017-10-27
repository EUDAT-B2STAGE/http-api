
# Other operations

Here we have more informations for further debugging/developing the project


## launch interfaces

To explore data and query parameters there are few other services as options:

```bash
SERVER=localhost  # or your IP / Domain
PORT=8080

# access a swagger web ui
rapydo interfaces swagger
# access the webpage:
open http://$SERVER/swagger-ui/?url=http://$SERVER:$PORT/api/specs

# SQL admin web ui
rapydo interfaces sqlalchemy
# access the webpage:
open http://$SERVER:81/adminer
```

## add valid b2handle credentials

To resolve non-public `PID`s prefixes for the `EPIC HANDLE` project we may leverage the `B2HANDLE` library providing existing credentials. 

You can do so by copying such files into the dedicated directory:

```bash
cp PATH/TO/YOUR/CREDENTIALS/FILES/* data/b2handle/
```

## destroy all

If you need to clean everything you have stored in docker from this project:

```bash
# BE CAREFUL!
rapydo clean --rm  # very DANGEROUS
# With this command you lose all your current data!
```

## hack the certificates volume

This hack is necessary if you want to raw copy a Certification Authority credential. 
It may be needed if your current B2SAFE host DN was produced with an internal certification authority which is not recognized from other clients.

```bash
path=`docker inspect $(docker volume ls -q | grep sharedcerts) | jq -r ".[0].Mountpoint"`
sudo cp /PATH/TO/YOUR/CA/FILES/CA-CODE.* $path/simple_ca

```