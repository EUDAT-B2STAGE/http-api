
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
# TODO: decide about a main user recipe for containers
ENV APIUSER developer
ENV CERTDIR /opt/certificates
# Emulating irods user creation. See http://j.mp/2lGPqlq
RUN useradd -r -M -d $CERTDIR/home -s /bin/bash -p ! $APIUSER
# Adding gsi as gssapi available mechanism for RPC
COPY gsi.conf /etc/gss/mech.d/

# TO FIX: on the irods side?
# usermod -m -d  username

###################
# Closing entrypoint

RUN mkdir /code
WORKDIR /code
RUN mkdir /docker-entrypoint.d/
RUN echo "alias httpapi=\"su -p \$APIUSER -c 'cd /code; python run.py'\"" >> /root/.bash_aliases
RUN echo "alias testapi=\"su -p \$APIUSER -c 'cd /code; nose2 -F '\"" >> /root/.bash_aliases

COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint
ENTRYPOINT ["docker-entrypoint"]
CMD ["rest"]
ENV PAGER less
ENV TERM=xterm-256color
ENV PYTHONIOENCODING="utf-8"
# Flask port
EXPOSE 5000

RUN echo "Entrylevel" && \
    echo "echo\necho 'Run Flask server as ($APIUSER) with the command:'\necho '$ httpapi'" >> /root/.bashrc && \
    echo "echo\necho 'Run tests also with:\n$ testapi [test.FOLDER]'\n\n" \
    >> /root/.bashrc
