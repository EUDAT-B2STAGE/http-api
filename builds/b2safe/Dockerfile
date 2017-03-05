
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
        ## fix the plugin error at irods installation time
        libxml2 \
    # clean
    && apt-get clean autoclean && apt-get autoremove -y && \
    rm -rf /var/lib/cache /var/lib/log /tmp/*

# Add repos, download and install
ENV URL https://packages.irods.org
RUN apt-key adv --fetch-keys $URL/irods-signing-key.asc \
    # && echo "deb $URL/apt/ $(lsb_release -sc) main" \
    && echo "deb $URL/apt/ trusty main" \
        > /etc/apt/sources.list.d/renci-irods.list

ENV IRODS_VERSION 4.2.0
RUN apt-get update && apt-get install -y \
        # iCAT
        irods-server=$IRODS_VERSION \
        # iRODS Plugins (also GSI)
        irods-database-plugin-postgres irods-auth-plugin-gsi \
    # clean
    && apt-get clean autoclean && apt-get autoremove -y && \
    rm -rf /var/lib/cache /var/lib/log /tmp/*

# Note: USER and GROUP are added automatically by irods install scripts

#######################################
## Closing operations

ENV TERM xterm-256color

# RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
# # User 'guest' for testing certificates
# ENV GSI_USER guest
# RUN useradd -ms /bin/bash $GSI_USER
# WORKDIR /home/$GSI_USER
# COPY guest.irods.env.json .irods/irods_environment.json
# RUN chown -R $GSI_USER:$GSI_USER /home/$GSI_USER/.irods
# # rodsminer for administration with GSI auth
# ENV GSI_ADMIN rodsminer
# RUN useradd -ms /bin/bash $GSI_ADMIN
# COPY new_authority.sh /addusercert
# COPY certificates_init.sh /init_certificates

# if you need to add future commands after irods installation:
ENV EXTRA_INSTALLATION_SCRIPT /extras

# VOLUMES
VOLUME /etc
VOLUME /var/lib/irods
# Not needed because irods home is var/lib/irods!!
# VOLUME /home/$IRODS_USER

COPY ./expect_irods.sh /prepare_answers
COPY ./docker-entrypoint.sh /

EXPOSE 1247
WORKDIR /tmp
ENTRYPOINT ["/docker-entrypoint.sh"]
