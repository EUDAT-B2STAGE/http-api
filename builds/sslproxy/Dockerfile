
# PROXY that accepts challenges
FROM nginx:1.11.13-alpine
MAINTAINER "Paolo D'Onorio De Meo <p.donorio.demeo@gmail.it>"

RUN apk update && \
    apk add wget git openssl \
    && rm -rf /var/cache/apk/*

WORKDIR /tmp
# TO FIX: choose the right directory for installation
ENV ACMEDIR /acme
ENV ACMEV "2.6.6"
# TO FIX: clone on a certain release/commit
RUN echo acme && \
    # git clone https://github.com/Neilpang/acme.sh.git \
    wget https://github.com/Neilpang/acme.sh/archive/2.6.6.zip \
    && unzip ${ACMEV}.zip && cd acme.sh-${ACMEV} \
    && ./acme.sh --install --home $ACMEDIR \
    && cd .. && rm -rf *$ACMEV

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
