
# Quick start

Up and running in five minutes:

```bash

# start from the latest release
git clone https://github.com/EUDAT-B2STAGE/http-api.git
cd http-api

# install the controller and other libs
pip3 install --upgrade -r projects/eudat/requirements.txt

- check the framework
rapydo check --skip-heavy-git-ops

# fix what is missing from above
rapydo init

# run containers in background
rapydo --force-env control start

# WARNING: TEMPORARY FIX
sleep 10 && rapydo --services backend shell --command initialize

# launch http-api server 
rapydo --services backend shell --command rapydo

# now access a client into another shell
rapydo --services restclient shell --user developer

# clean everything
rapydo clean --rm-volumes  # very DANGEROUS!

```
