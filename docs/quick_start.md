
# Quick start

This is a reference page to quick start your knowledge of the project.


## Using the prototype online

The quickest way to deploy or develop the current project state is to test online our [prototype](https://b2stage-test.cineca.it/api/status). 
Also see the [dedicated instructions](prototype.md). Please feel free [to report or comment](https://gitter.im/EUDAT-B2STAGE/http-api) to help us improve!


## Set-up your "debug" instance (in very few commands)

If you feel comfortable with a terminal shell you could spin your first instace easily. Please head to the [pre-requisites](deploy/preq.md) page first, to make sure your current machine is qualified to host the project.

NOTE: **DO NOT** run this instructions as administrator. Please make sure you are not the `root` user (e.g. with the `whoami` command); this behaviour is not allowed by the `rapydo` framework.

Here's step-by-step tutorial to work with the HTTP API project:
```bash

################
# get the code
git clone https://github.com/EUDAT-B2STAGE/http-api.git latest
cd latest
git checkout 1.0.3

################
# install the corrensponding rapydo framework version
sudo -H data/scripts/prerequisites.sh
# build and run
rapydo init
rapydo start

################
# only required in debug mode
rapydo shell backend --command 'restapi launch'
```

If everything worked so far you may now try a test against your own server:
```bash
# from another shell
$ curl -i localhost:8080/api/status

HTTP/1.0 200 OK
Content-Type: application/json
Access-Control-Allow-Origin: *
Content-Length: 185
Server: Werkzeug/0.12.2 Python/3.6.3
Date: Tue, 05 Dec 2017 15:56:40 GMT

{
  "Meta": {
    "data_type": "<class 'str'>",
    "elements": 1,
    "errors": 0,
    "status": 200
  },
  "Response": {
    "data": "Server is alive!",
    "errors": null
  }
}
```


## Production

The key difference to switch from debug to production `mode` for the previuos commands is by passing the dedicated option to `rapydo`, e.g. `rapydo --mode production start`.

To ensure the option is always activated you can save it in a `.projectrc` file:

```bash

# setup a rc file to save your preferred rapydo options
echo "project: b2stage" > .projectrc
echo "mode: production" >> .projectrc
echo "hostname: yourdomain.com" >> .projectrc  # set a domain if you have one
```

You can override any of the project configuration variables, e.g. to set an external B2SAFE instance by including a project_configuration section into your .projectrc file.

```bash
project: b2stage
mode: production
hostname: yourdomain.com
project_configuration:
  variables:
    env:
      IRODS_HOST: your.b2safe.host
```

You can now start your HTTP api server in production mode.

```bash
# remove containers in debug mode
rapydo remove

rapydo start  # in production, thanks to the projectrc setup
# Hint: double check open ports 80 and 443 from the outside world

# issues a valid free SSL certificate with "Let's Encrypt"
rapydo ssl-certificate  

# check your server is alive and running on HTTPS protocol
curl -i https://YOURDOMAIN.com/api/status

# check your swagger configuration with a browser
open http://petstore.swagger.io/?url=https://YOURDOMAIN.com/api/specs&docExpansion=none
```


### Periodically update the SSL certificate

Certificates issued using "Let's encrypt" lasts 90 days.
To make sure your certificate is always up-to-date you can setup a cron job to run every two months of the year.

```bash

# edit crontab
$ crontab -e

# add this line
30  0   1   2,4,6,8,10,12  *    cd /path/to/httpapi/code && rapydo ssl-certificate
# runs the 1st day of even months of the year, at 00:30 AM

# to check later on about cron jobs executions:
less /var/log/cron
```

## Other actions

We implemented on the `rapydo` cli tool all needed Docker (or Docker compose) typical actions to manage running containers: `rapydo status`, `rapydo stop`, `rapydo remove`.

To get a list of all available commands you can use one of the following:
```bash
rapydo
rapydo --help
rapydo -h
```


## What's more

Finally to dig more into details you may now [head back to the index](README.md#documentation) to read the other parts of the documentation.
