
# Quick start

This is a reference page to quick start your knowledge of the project.


## Using the prototype online

The quickest way to deploy or develop the current project state is to test online our [prototype](https://b2stage-test.cineca.it/api/status). 
Also see the [dedicated instructions](prototype.md). Please feel free [to report or comment](https://gitter.im/EUDAT-B2STAGE/http-api) to help us improve!


## A debug instance in few commands

If you feel comfortable with a terminal shell you could spin your first instace easily. Please head to the [pre-requisites](docs/deploy/preq.md) page first, to make sure your host is qualified to host the project.

Here's step-by-step tutorial to work with the HTTP API project:
```bash

################
# get the code
git clone https://github.com/EUDAT-B2STAGE/http-api.git latest
cd latest
git checkout 1.0.1

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

# remove containers in debug mode
rapydo remove

# setup a rc file to save your preferred rapydo options
echo "project: b2stage" > .projectrc
echo "mode: production" >> .projectrc
echo "hostname: yourdomain.com" >> .projectrc  # set a domain if you have one

# edit the project configuration to set an external B2SAFE instance
vi projects/b2stage/project_configuration.yaml

rapydo start  # in production
rapydo ssl-certificate  # issue valid certificate with "Let's Encrypt"
curl -i https://yourdomain.com/api/status
```

To dig more into details you may now [head back to the index](https://github.com/EUDAT-B2STAGE/http-api/blob/1.0.1/README.md#documentation).
