
## Development operations

A set of snippets that helped in the past.


### test irods auth proxy

Create users (also in different iRODS zones) and test them with the proxy from the HTTP API:

```bash
rapydo shell icat

berods
ZONE1=$IRODS_ZONE
ZONE2=anotherZone
iadmin mkzone $ZONE2 remote

USER=paolobeta
PASS=thisisalongerpassword
iadmin mkuser $USER rodsuser
iadmin moduser $USER password $PASS
iadmin mkuser $USER#$ZONE2 rodsuser
```

and in another shell

```bash 
rapydo shell restclient

USER=paolobeta
PASS=thisisalongerpassword

http POST $APP_HOST$APP_PORT/auth/b2safeproxy username=$USER password=$PASS

# TOKEN=$(http POST localhost:8080/auth/b2safeproxy \
#    username=$USER password=$PASS | jq .Response.data.token | tr -d '"')

# http localhost:8080/auth/b2safeproxy Authorization:"Bearer $TOKEN"
```


### squash branch

A better practice before pull requesting is to squash commits into a single one. Here's a guide on how to do so with git cli:

```bash
MYEXISTINGBRANCH='v0.1.0'
BASEBRANCH='master'

# start from the base branch (usually it's master)
git checkout $BASEBRANCH
# create a new branch for squashing
git checkout -b ${MYEXISTINGBRANCH}-squashed
# squash the differences between now and the feature branch
git merge --squash $MYEXISTINGBRANCH
# commit message will contain all commit messages so far
git commit
# you may/should change the content, at least top title and description
```