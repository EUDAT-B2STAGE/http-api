
# For developers

If you use `restangulask` as a base for your project,
this page will help you through.

## Switch app mode/level

Edit `containers/docker-compose.yml`.
Choose the `APP_MODE` variable which will be reflected to all containers:

* `production`
* `development` (no real dbs, sqllite and flask in restartable mode)
* `debug` (containers start with sleep instead of running commands)

Note: if you use debug, to start the app inside the container:

```bash
$ docker ps
# see the name of the container you need to debug
$ docker exec -it CONTAINER_NAME bash
# ./boot devel
```

## Install a new package via bower

In case you need to add some angular module, if not provided yet:

```bash
./boot.sh bower PACKAGE_NAME
```

## Push changes to Git repo

Add manually only the files inside the main repo
you need to commit. Then:

```bash
# Commit all submodules and also main repo
./push
```
