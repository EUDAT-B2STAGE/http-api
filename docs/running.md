
# Deploying your services

### Run the final services

Following the previous section everything should be properly configured.
You can launch postgresql & irods - from now on - with this simple comand:

```bash
$ docker-compose up -d

Recreating irods_sql_1
Recreating irods_icat_1
```

### Verify services and ports

Checking processes with compose must say that both containers are up:
```bash
$ docker-compose ps
    Name                  Command               State    Ports
----------------------------------------------------------------
irods_icat_1   /bootstrap                       Up      1247/tcp
irods_sql_1    /docker-entrypoint.sh postgres   Up      5432/tcp
```

### Opening a shell inside the iRODS iCat server

```bash
$ docker exec -it irods_icat_1 bash
irods@rodserver:~$ ils
/tempZone/home/rods:
```

### Restarting the irods server

```bash
$ docker exec -t irods_icat_1 /etc/init.d/irods restart
```

### Accessing your irods server from outside the Docker network

1) Remove comments from this lines inside `docker-compose.yml`:

```yaml
    # ports:
    #     - 1247:1247
```

2) Access the irods host as `rodserver`

e.g. you have your host ip as 130.1.2.10, add this line to `/etc/hosts`:
```
130.1.2.10 rodserver
```

3) Be sure you open port 1247 on every firewall your host works behind

### Connecting to irods with another container as a client

You may launch a new container using the same docker image.
This will allow you to access the latest icommands to test
a connection from outside.

```bash
$ docker run -it --link irods_icat_1:rodserver cineca/icat bash
# then from inside the new container...

# See what is the current passw
echo $IRODS_PASS

# Use the defaults values
$ iinit
Enter the host name (DNS) of the server to connect to: rodserver
Enter the port number: 1247
Enter your irods user name: rods
Enter your irods zone: tempZone
Enter your current iRODS password: # the one above
```

You can now go to [next chapter](client.md).

*A security note*:

The main password is saved as an environment variable for development purpose.
We will provide a way to change it in further development.
Anyway, security for containers is best reached by avoiding connections/launching
 containers from outside your net/LAN.
