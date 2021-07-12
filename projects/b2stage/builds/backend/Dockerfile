FROM rapydo/backend:2.0
MAINTAINER "Mattia D'Antonio <m.dantonio@cineca.it>"

ARG RAPYDO_VERSION
RUN test -n "$RAPYDO_VERSION"

#########################################################
# Python 3.9 is not working for gssapi 1.5.1, let's downgrade to python 3.8
ENV PYTHON_VERSION="3.8"
RUN ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 \
    && curl --silent https://bootstrap.pypa.io/get-pip.py --output get-pip.py \
    && python3 get-pip.py \
    && rm get-pip.py \
    && apt-get update \
    && apt-get install --yes python${PYTHON_VERSION}-dev \
    && pip3 install --upgrade --no-cache-dir watchdog[watchmedo]==2.1.3 git+https://github.com/rapydo/http-api.git@$RAPYDO_VERSION
#########################################################

RUN apt-get update \
 && apt-get install -y zip libkrb5-dev unzip \
 && apt-get autoremove \
 && apt-get clean

RUN pip3 install --upgrade --no-cache-dir oauthlib==2.1.0 Werkzeug==0.16.1 requests-oauthlib==1.1.0 Flask-OAuthlib==0.9.5 Authlib==0.14.1 git+https://github.com/EUDAT-B2STAGE/B2HANDLE.git@master python-irodsclient==0.8.4 gdapi-python==0.5.3 gssapi==1.5.1
