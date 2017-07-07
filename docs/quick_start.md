
# Quick start

## Download and deploy for development


```bash
# up and running in 5 minutes

# start from the latest release
git clone https://github.com/EUDAT-B2STAGE/http-api.git
cd http-api

# install the controller and other libs
pip3 install --upgrade -r projects/eudat/requirements.txt

# check the framework
rapydo check --skip-heavy-git-ops

# fix what is missing from above
rapydo init

# run containers in background
rapydo start

# operations inside backend
rapydo shell backend
$ initialize
# develop separated scripts
$ python3.6 eudat/project/filldb.py
# launch http-api server 
$ rapydo

# now access a client into another shell
rapydo shell restclient --user developer

# access mongo admin web ui
rapydo interfaces mongo
# then open http://localhost

# access a swagger web ui
rapydo interfaces swagger
# then open http://localhost:81/swagger-ui/?url=http://localhost:8080/api/specs

# clean everything
rapydo clean --rm-volumes  # very DANGEROUS!

```


## Squash branch

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
