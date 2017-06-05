
git clone https://github.com/EUDAT-B2STAGE/http-api.git
cd http-api

rapydo check

rapydo init

rapydo control start

# launch 
rapydo --services backend shell --command rapydo

# clean everything
## DANGEROUS!
rapydo clean --rm-volumes

