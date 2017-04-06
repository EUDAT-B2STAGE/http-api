
FROM python:3.6-alpine
# FROM alpine:edge

MAINTAINER "Paolo D'Onorio De Meo <p.donoriodemeo@cineca.it>"
# Note:
# This is image is intended to be as small as possible

RUN apk update && apk upgrade && apk add \
    bash less vim \
    curl wget git \
    jq \
    && rm -rf /var/cache/apk/*

# # Install pip
# RUN wget -q https://bootstrap.pypa.io/get-pip.py \
#     && python3 get-pip.py && rm *.py

# Install python packages
RUN pip --no-cache-dir install --upgrade \
    pip httpie http-prompt pyyaml

# Install jqt/yq
# https://fadado.github.io/jqt/
RUN git clone https://github.com/fadado/jqt.git /tmp/jqt \
    && ln -s /usr/local/bin/python /usr/bin/
ENV PATH $PATH:/tmp/jqt/bin

###################################
RUN mkdir -p /code/client
WORKDIR /code/client
RUN mkdir /docker-entrypoint.d/
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint
ENTRYPOINT ["docker-entrypoint"]
CMD ["client"]

# Handle a guest user
ENV GUEST_USER developer
ENV GUEST_UID 1000
ENV GUEST_SHELL /bin/bash
RUN adduser -s $GUEST_SHELL -u $GUEST_UID -D -h /home/$GUEST_USER $GUEST_USER

# Script for automatic creation of a token
COPY client_init.sh /code/gettoken
COPY query_api.sh /code/queryapi
# RUN echo -e "#!/bin/bash\nsource /code/queryapi $1\n" > /usr/bin/queryapi \
#     && chmod +x /usr/bin/queryapi

# Use the new user
USER $GUEST_USER
ENV BASHRC /home/$GUEST_USER/.bashrc
ENV PAGER less
ENV TERM=xterm-256color
ENV HISTCONTROL ignoreboth:erasedups
RUN echo "echo -e '\\nCall the client with the command:'" >> $BASHRC \
    # && echo "echo -e '$ queryapi\\n'" >> $BASHRC \
    && echo "echo -e '$ . /code/queryapi [help]\\n'" >> $BASHRC
