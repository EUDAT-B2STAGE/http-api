
FROM ubuntu:16.04
# LTS
MAINTAINER "Paolo D'Onorio De Meo <p.donoriodemeo@cineca.it>"

# Preparation
RUN apt-get update -qq && apt-get install -y \
        ## normal base
        wget git vim expect lsof sudo \
        ## fix adding irods to source list
        # lsb-release \
        ## fix the ssl error for apt-key
        gnupg-curl \
        ## fix "The method driver /usr/lib/apt/methods/https could not be found"
        apt-transport-https \
    # clean
    && apt-get clean autoclean && apt-get autoremove -y && \
    rm -rf /var/lib/cache /var/lib/log /tmp/*

# Add repos, download and install
ENV URL https://packages.irods.org
RUN apt-key adv --fetch-keys $URL/irods-signing-key.asc \
    # && echo "deb $URL/apt/ $(lsb_release -sc) main" \
    && echo "deb $URL/apt/ trusty main" \
        > /etc/apt/sources.list.d/renci-irods.list \
    && apt-get update && apt-get install -y \
        irods-server irods-database-plugin-postgres

# INSTALL GSI

# Note: USER and GROUP are added automatically by irods install scripts

# Configuration schemas now included
# Default setups will no longer need a public network connection for validation
