
###################
FROM ubuntu:17.10
LABEL maintainer="Paolo D'Onorio De Meo <p.donoriodemeo@cineca.it>"

##############
### HOW TO ###

## CREATE A USER
# iadmin mkuser paolo rodsuser
# iadmin moduser paolo password tester

## CLOCK SYNC ISSUES
# apt-get install -y tzdata
# unlink /etc/localtime
# ln -s /usr/share/zoneinfo/Etc/GMT+6 /etc/localtime

###################
# Preparation
WORKDIR /tmp
RUN apt-get update -qq && apt-get install -y \
        zip zipmerge \
        wget git vim apt-transport-https libxml2 \
    && apt-get clean autoclean && apt-get autoremove -y && \
    rm -rf /var/lib/cache /var/lib/log /tmp/*

###################
# Add repos, download and install
ENV URL https://packages.irods.org
RUN wget -qO - $URL/irods-signing-key.asc | apt-key add - \
    && echo "deb [arch=amd64] https://packages.irods.org/apt/ trusty main" | tee /etc/apt/sources.list.d/renci-irods.list

ENV IRODS_VERSION 4.2.1
# ENV IRODS_VERSION 4.2.2

# ENV IRODS_UNAME irods
# # ENV IRODS_UID 990
# ENV IRODS_UID 1001
# RUN useradd \
#     -r -M -d /home/$IRODS_UNAME -s /bin/bash -p ! \
#     --uid $IRODS_UID $IRODS_UNAME \
#     && mkdir -p /home/$IRODS_UNAME && chown $IRODS_UID /home/$IRODS_UNAME

RUN apt-get update && apt-get install -y \
        irods-runtime=$IRODS_VERSION \
        irods-icommands=$IRODS_VERSION \
    && apt-get clean autoclean && apt-get autoremove -y && \
    rm -rf /var/lib/cache /var/lib/log /tmp/*

###################
# dumb init
RUN wget https://github.com/Yelp/dumb-init/releases/download/v1.2.1/dumb-init_1.2.1_amd64.deb \
    && dpkg -i dumb-init_*.deb \
    && rm *.deb
ENV TERM xterm-256color
# ENTRYPOINT
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
RUN mkdir /docker-entrypoint.d/
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint

# command
RUN chmod +x /usr/local/bin/*
# CMD ["docker-entrypoint", "download"]
# CMD ["docker-entrypoint", "upload"]
CMD ["docker-entrypoint", "addzip"]

# NOTE: using root to adjust batch dir permissions
# USER $IRODS_UNAME

ENV LINES 28
ENV COLUMNS 160
