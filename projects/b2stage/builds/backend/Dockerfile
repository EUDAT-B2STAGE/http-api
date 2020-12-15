FROM rapydo/backend:0.9
MAINTAINER "Mattia D'Antonio <m.dantonio@cineca.it>"

RUN apt-get update \
 && apt-get install -y zip libkrb5-dev unzip \
 && apt-get autoremove \
 && apt-get clean

RUN pip3 install --upgrade --no-cache-dir oauthlib==2.1.0 Werkzeug==0.16.1 requests-oauthlib==1.1.0 Flask-OAuthlib==0.9.5 Authlib==0.14.1 git+https://github.com/EUDAT-B2STAGE/B2HANDLE.git@master python-irodsclient==0.8.4 gdapi-python==0.5.3 gssapi==1.5.1
