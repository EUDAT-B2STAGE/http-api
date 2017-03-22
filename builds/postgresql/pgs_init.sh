#!/bin/bash

conf='/var/lib/postgresql/data/pg_hba.conf'
## TO FIX: from an environment variable
net="172.1.0.0/16"
## http://www.postgresql.org/docs/9.1/static/auth-pg-hba-conf.html

echo "Changing access"
echo "" > $conf

# Enable to allow health checks
echo "local   $POSTGRES_USER  $POSTGRES_USER  trust" >> $conf

echo "hostnossl       postgres  $POSTGRES_USER  $net   password" >> $conf

###################
# DBs handling
for obj in $POSTGRES_DBS;
do
    db=$(echo $obj | tr -d "'")
    echo "Enabling DB $db"
# Create it
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" << EOSQL
    CREATE DATABASE "$db";
EOSQL
    # GRANT ALL PRIVILEGES ON DATABASE "$db" TO $POSTGRES_USER;
# Add privileges
echo "hostnossl       $db  $POSTGRES_USER  $net   password" >> $conf
done

###################
echo "DONE"

## In case you need to startup a database

# echo "******CREATING DATABASE******"
# gosu postgres postgres --single << EOSQL
# CREATE USER docker WITH SUPERUSER PASSWORD 'test';
# #CREATE ROLE docker CREATEDB LOGIN PASSWORD 'test';
# # CREATE DATABASE docker;
# # CREATE USER docker WITH ENCRYPTED PASSWORD 'test';
# # GRANT ALL PRIVILEGES ON DATABASE docker to docker;
# EOSQL
