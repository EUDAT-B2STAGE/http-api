
echo "Create directory [POST]"
http --form POST \
    $SERVER/api/resources?path=/tempZone/home/guest/test \
    force=True "$AUTH"
if [ "$?" != "0" ]; then echo "ERROR"; exit 1; fi

echo "Upload file [PUT]"
http --form PUT $SERVER/api/resources/tempZone/home/guest/test \
    file@/tmp/gettoken force=True "$AUTH"
if [ "$?" != "0" ]; then echo "ERROR"; exit 1; fi

echo "Remove file [DELETE]"
http DELETE \
    $SERVER/api/resources/tempZone/home/guest/test/gettoken "$AUTH"
if [ "$?" != "0" ]; then echo "ERROR"; exit 1; fi

echo "Remove directory [DELETE]"
http DELETE \
    $SERVER/api/resources/tempZone/home/guest/test "$AUTH"
if [ "$?" != "0" ]; then echo "ERROR"; exit 1; fi
