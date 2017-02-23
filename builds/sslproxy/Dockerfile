
# PROXY that accepts challenges
FROM nginx:1.11-alpine
MAINTAINER "Paolo D'Onorio De Meo <p.donoriodemeo@cineca.it>"

RUN apk update && \
    apk add wget git openssl \
    && rm -rf /var/cache/apk/*

WORKDIR /tmp
# TO FIX: choose the right directory for installation
ENV ACMEDIR /root/.acme.sh
# TO FIX: clone on a certain release/commit
RUN git clone https://github.com/Neilpang/acme.sh.git \
    && cd acme.sh && \
    ./acme.sh --install \
    && cd .. && rm -rf acme.sh

RUN mkdir -p /usr/share/nginx/html/.well-known/acme-challenge
RUN chown -R nginx /usr/share/nginx/html

# Set the directory for launching the renewall script
WORKDIR $ACMEDIR

# Save production certificates across multiple run
VOLUME /etc/letsencrypt
ENV CERTDIR /etc/letsencrypt/real
ENV WWWDIR /usr/share/nginx/html
RUN mkdir -p $CERTDIR

# Configure nginx on basic aspects
# + read configurations in "sites-enabled" dir
ADD nginx.conf /etc/nginx/nginx.conf
ADD letsencrypt.sh /updatecertificates
