
if [ -z "$CREDENTIALS" ]; then
    echo "No credentials provided via environment!"
    echo "Please set the variable \$CREDENTIALS"
    return
fi

# NOTE: this has been modified
# export SERVER="$APP_HOST:$APP_PORT"
export SERVER="$APP_HOST$APP_PORT"
echo "Using server $SERVER"

echo "Login"
# export CREDENTIALS="username=user@nomail.org password=test"
TOKEN=`http POST $SERVER/auth/login $CREDENTIALS | jq '.Response.data.token' | tr -d '"'`

if [ "$TOKEN" == "" ]; then
    echo ""
    echo "Failed to connect to Flask server..."
elif [ "$TOKEN" == "null" ]; then
    echo ""
    echo "Invalid credentials"
else
    echo "Logged"
    export AUTH="Authorization:Bearer $TOKEN"

    echo "You can now query the API SERVER. Examples:"
    echo ""
    echo "- Query the status endpoint and parse the JSON response"
    echo '$ http GET $SERVER/api/status | jq "."'
    echo ""
    echo "- Query a protected endpoint by passing the saved token"
    echo '$ http GET $SERVER/auth/profile "$AUTH"'
fi
echo ""
