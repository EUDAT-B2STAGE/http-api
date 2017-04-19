
# PROXY that accepts challenges
FROM nginx:1.11.13-alpine
MAINTAINER "Paolo D'Onorio De Meo <p.donoriodemeo@cineca.it>"

RUN apk update && \
    apk add vim wget git bash \
    openssl curl netcat-openbsd \
    && rm -rf /var/cache/apk/*

WORKDIR /tmp
# TO FIX: choose the right directory for installation
ENV ACMEDIR /acme
ENV ACMEV "2.6.8"

########################
# RUN curl https://get.acme.sh | sh

# RUN echo acme && \
#     wget https://github.com/Neilpang/acme.sh/archive/${ACMEV}.zip \
#     && unzip ${ACMEV}.zip

RUN echo acme && \
    # git clone https://github.com/Neilpang/acme.sh.git \
    wget https://github.com/Neilpang/acme.sh/archive/${ACMEV}.zip \
    && unzip ${ACMEV}.zip && cd acme.sh-${ACMEV} \
    && ./acme.sh --install --home $ACMEDIR \
    && cd .. && rm -rf *$ACMEV

#######################
RUN mkdir -p /usr/share/nginx/html/.well-known/acme-challenge
RUN chown -R nginx /usr/share/nginx/html

# Set the directory for launching the renewall script
WORKDIR $ACMEDIR

# Save production certificates across multiple run
ENV WWWDIR /usr/share/nginx/html
ENV CERTDIR /etc/letsencrypt/real
ENV CERTKEY ${CERTDIR}/privkey1.pem
ENV CERTCHAIN ${CERTDIR}/fullchain1.pem
RUN mkdir -p $CERTDIR
VOLUME /etc/letsencrypt

# Configure nginx on basic aspects
# + read configurations in "sites-enabled" dir
COPY nginx.conf /etc/nginx/nginx.conf
COPY letsencrypt.sh /usr/local/bin/updatecertificates
COPY create_self_signed_ssl.sh /usr/local/bin/selfsign

###################
# closing entrypoint
RUN mkdir /docker-entrypoint.d
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint
ENTRYPOINT ["docker-entrypoint"]
CMD ["proxy"]
