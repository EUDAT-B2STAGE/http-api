#!/bin/bash

vault_path="/mnt/data1/irods/Vault/cloud"
irods_path="/sdcCineca/cloud"
import_prefix="import30may_rabbithole_500000_"
pid_prefix="21.T12995"
out_file="./pids.txt"

rm -f $out_file

for dir in $(ls -1d ${vault_path}/${import_prefix}*);
do
    for element in $(ls -1 $dir/*);
    do
        # echo $element
        fname=$(basename $element)
        dpath=$(dirname $element)
        dname=$(basename $dpath)
        pid=$(imeta ls -d $irods_path/$dname/$fname | grep $pid_prefix)
        echo -e "$dname\t$fname\t$pid" >> $out_file
        # break
    done
    # break
done

