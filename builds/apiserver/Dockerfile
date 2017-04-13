
###################
# FROM eudatb2stage/apiserver:neo4j3
FROM ubuntu:17.04
# FROM python:3.6-alpine
MAINTAINER "Paolo D'Onorio De Meo <p.donoriodemeo@cineca.it>"

###################
# APT
RUN apt-get update && apt-get install -y \
    # utils
    bash less vim curl wget telnet git jq \
    # latest python
    python3.6 \
    # build dependencies for gssapi plugin (GSI and irods)
    build-essential libkrb5-dev python3.6-dev \
    libglobus-gssapi-gsi-dev \
    # make this version the official python for anyone
    && cd /usr/bin && ln -s python3.6 python \
    && apt-get autoremove && apt-get clean \
    && echo "done"

###################
# PIP

WORKDIR /tmp
RUN wget -q https://bootstrap.pypa.io/get-pip.py \
    && python get-pip.py && rm *.py

COPY requirements.txt /tmp/
RUN pip3 install --upgrade \
    --force-reinstall --no-cache-dir -r requirements.txt

###################
# Adding gsi as gssapi available mechanism for RPC
COPY gsi.conf /etc/gss/mech.d/
# main user for launching the apis
ENV APIUSER developer
ENV CERTDIR /opt/certificates
# Emulating irods user creation. See http://j.mp/2lGPqlq
RUN useradd -r -M -d $CERTDIR/home -s /bin/bash -p ! $APIUSER

###################
# variables
ENV PAGER less
ENV TERM=xterm-256color
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHONIOENCODING="utf-8"
ENV FLASK_PORT 5000
ENV JWT_APP_SECRETS /jwts
EXPOSE $FLASK_PORT

######################
# alias
RUN echo "alias dev=\"HOME=/tmp su -p \$APIUSER\"" >> /root/.bash_aliases
RUN echo "alias testapi=\"su -p \$APIUSER -c 'export HOME=/tmp; cd /code; nose2 -F '\"" >> /root/.bash_aliases

RUN echo "#!/bin/bash\\nsu -p \$APIUSER -c 'export HOME=/tmp; cd /code; ./tests.sh'" > /usr/local/bin/testwithcoverage && chmod +x /usr/local/bin/testwithcoverage
RUN echo "#!/bin/bash\\nsu -p \$APIUSER -c 'export HOME=/tmp; cd /code; flask run --with-threads -h 0.0.0.0 -p $FLASK_PORT '" > /usr/local/bin/rapydo && chmod +x /usr/local/bin/rapydo
RUN echo "#!/bin/bash\\nsu -p \$APIUSER -c 'export HOME=/tmp; cd /code; FLASK_DEBUG=0 ./manage.py init'" > /usr/local/bin/initialize && chmod +x /usr/local/bin/initialize
RUN echo "#!/bin/bash\\nsu -p \$APIUSER -c 'export HOME=/tmp; cd /code; FLASK_DEBUG=0 ./manage.py destroy'" > /usr/local/bin/demolition && chmod +x /usr/local/bin/demolition

######################
# instructions
RUN echo "Entrylevel" && \
    echo "echo\necho 'Run Flask server as ($APIUSER) with the command:'\necho '$ rapydo'" >> /root/.bashrc && \
    echo "echo\necho 'Run tests also with:\n$ testapi [test.FOLDER]\n'\n" \
        >> /root/.bashrc \
    && echo "echo\necho '$ python run.py'" > /tmp/.bashrc

###################
# closing entrypoint

RUN mkdir /code
WORKDIR /code
RUN mkdir /docker-entrypoint.d/
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint
ENTRYPOINT ["docker-entrypoint"]
CMD ["rest"]
