
# Quick start

Up and running in five minutes:

```bash
# start from the latest release
git clone https://github.com/EUDAT-B2STAGE/http-api.git
cd http-api

# check the framework
rapydo check

# fix what is missing from above
rapydo init

# run containers in background
rapydo control start

# launch http-api server 
rapydo --services backend shell --command rapydo

# client
rapydo --services restclient shell --user developer

# clean everything
rapydo clean --rm-volumes  # very DANGEROUS!

```
