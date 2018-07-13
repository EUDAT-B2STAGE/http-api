
container='some-container-hash'

######################
# Dump into tar gz
docker exec -it $container bash -c 'mongodump --out /data/backup'
docker exec -it $container bash -c 'tar cvzf /tmp/rocket.backup.tar.gz /data/backup/rocketchat'
docker cp $container:/tmp/rocket.backup.tar.gz /tmp/

######################
# Restore

# tar xzvf rocket.backup.tar.gz
# mongorestore data/backup/
