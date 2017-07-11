
# Quick start

This is a reference page to quick start the HTTP API project.

## Deploy for development

A minimum set of operations to start developing within this repository:


```bash

# start from the latest release
git clone https://github.com/EUDAT-B2STAGE/http-api.git
cd http-api

# install the controller and other libs
# this might require admin privileges
(sudo) pip3 install --upgrade -r projects/eudat/requirements.txt

# check the framework
rapydo check --skip-heavy-git-ops

# fix what is missing from above
rapydo init

# run containers in background
rapydo start

# operations inside backend
rapydo shell backend
# init all datas (e.g. authorization database)
$ initialize
# launch http-api server 
$ rapydo

# now you may access a client from another shell and test the server
rapydo shell restclient --user developer
```

The client shell will give you instructions on how to test the server


## Other operations

### Launch UIs to explore data

```bash
# access a swagger web ui
rapydo interfaces swagger
# then open http://localhost:81/swagger-ui/?url=http://localhost:8080/api/specs

# access admin web ui
rapydo interfaces sqlalchemy
# then open http://localhost:81/adminer
```


### Only for DEVELOPERS

#### Remove everything

```bash
# clean everything
rapydo clean --rm-volumes  # very DANGEROUS!
```


### Squash branch

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
