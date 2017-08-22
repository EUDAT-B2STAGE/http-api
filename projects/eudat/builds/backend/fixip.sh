#!/bin/bash

# workaround for not having a B2SAFE with a domain name registered in DNS
IP=""
NAME=""

if [ $(grep $IP /etc/hosts | wc -l) -ge "1" ];
    echo "ip already fixed inside backend"
else
    echo "$IP $NAME" >> /etc/hosts
fi
