#!/bin/bash

export TOKEN="blabla"
export SERVER='https://b2stage-test.cineca.it'
export APIHOME='/zone/home/user'
export inputfile='myfile'

for i in `seq 1 1024`;
do
        echo $i

        ## UPLOAD
        nohup dd if=/dev/zero of=$inputfile bs=1048576 count=10
        echo up $i
        curl -X PUT \
            -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/octet-stream" \
            -T $inputfile $SERVER/api/registered/$APIHOME/file${i}?force=true

        ## DOWNLOAD
        curl -o /tmp/file${i} \
            -H "Authorization: Bearer $TOKEN" \
            $SERVER/api/registered/$APIHOME/file${i}?download=true

done
