
# For developers

If you use `restangulask` as a base for your project,
this page will help you through.

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
