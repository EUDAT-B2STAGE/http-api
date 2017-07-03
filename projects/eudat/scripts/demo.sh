
## COMMANDS FOR A CLI DEMO OF API (from the restclient) ##

# check the status
curl $APP_HOST$APP_PORT/api/status
# or
http GET $APP_HOST$APP_PORT/api/status

# authenticate
http POST $APP_HOST$APP_PORT/auth/login username=user@nomail.org password=test

# save the token
export TOKEN="..."
export AUTH="Authorization:Bearer $TOKEN"

# create a collection/directory
http POST \
    $APP_HOST$APP_PORT/api/registered?path=/tempZone/home/guest/mydir "$AUTH"

# upload a file
http --form PUT \
    $APP_HOST$APP_PORT/api/registered/tempZone/home/guest/myfile \
    file@/tmp/jqt/VERSION "$AUTH"

