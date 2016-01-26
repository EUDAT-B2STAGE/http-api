
# Admin operations

## Manage postgres database

You may access an sqladmin interface based on 
[adminer](https://www.adminer.org/).

To launch the service:

```bash
docker-compose -f docker-compose.yml -f docker-compose.admin.yml up sqladmin
```

Then you may access http://localhost:8080 and insert all parameters for your
online database.

Note: if you use Mac/Windows you must check your Virtual Machine address,
instead of localhost. e.g.

```
# if you use toolbox/boot2docker
boot2docker ip
# if you use docker-machine
docker-machine ip MYMACHINE
```
