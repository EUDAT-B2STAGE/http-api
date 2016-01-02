
# Security

*This is a new feature!*

I integrated basic **Flask-Security** endpoints inside the REST API code.
This means that you may use Token based authentication
with triplets (user, pwd, role) saved in sqllite db.

Note: Security is enabled by default.
You can disable it with the option `--no-security` to the run script
(`run.py`).

To change it modify `docker-compose.py`.

## Endpoints

Flask-Security enables the following endpoints automatically:

* `/api/login` to authenticate a user and request a token
* `/api/logout` to release the token
* `/api/register` to request a user registration

This is the logic for a valid Token authentication request:
```bash
# Request a token with valid credentials
http awesome.dev:8081/login email=user@nomail.org password=test

[...]
"response": {
        "user": {
            "authentication_token": "WyIxIiwiOWQyMGRiMjVlY2YwMTE3YzQwOWY3YTNjOTRkYWFiYTkiXQ.CTeH2A.H-tktpx5coUan-msBGJGi_gicXw",
[...]

# Use the token
http awesome.dev:8081/api/checklogged Authentication-Token:WyIxIiwiOWQyMGRiMjVlY2YwMTE3YzQwOWY3YTNjOTRkYWFiYTkiXQ.CTeIMQ.3Jn4HI00zMgmH928glDPxcUss8w

[
    {
        "data": null,
        "data_type": null,
        "elements": 0
    },
]

```

<small>Note: i use [httpie](http://httpie.org) to test API endpoints.</small>

## Login with Python Requests

To get the token with Python requests:
[link to be added to script](../flasktests/client.py)

## Login with Javascript

A snippet to authenticate with Angular to our API:
```javascript
// To be written
```

## Admins

The **admin** user is the one how has `ROLE_ADMIN` associated in the relational db.
If you start from an empty DB, the code inject a first simple user with admin
privileges. Refer to [configuration](conf.md) if you need to change the default values.


## Admin interface

There is an automatic interface created with Flask-Admin.
Once the server is running in [security mode](run.md#security-mode) you can access
`/admin` endpoint with a browser (e.g.
[http://localhost:8081/api/manage](http://localhost:8081/api/manage)
)
to administrate users.

Of course you need to login with a valid **admin** user.
