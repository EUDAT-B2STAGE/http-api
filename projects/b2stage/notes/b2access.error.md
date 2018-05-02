
# B2ACCESS issue

## errors

HTTP API server side:

```bash
Catched exception <class 'gssapi.raw.exceptions.InvalidCredentialsError'>
2018-02-28 16:14:44,539 [WARNING b2stage.apis.commons.endpoint:157] GSS failure:
Major (655360): Invalid credential was supplied, Minor (6): GSS Minor Status Error Chain:
globus_gsi_gssapi: SSL handshake problems
globus_gsi_gssapi: Unable to verify remote side's credentials
globus_gsi_gssapi: SSL handshake problems: Couldn't do ssl handshake
OpenSSL Error: s3_both.c:415: in library: SSL routines, function ssl3_get_message: excessive message size
```

Client side:

```bash
{
    "Meta": {
        "data_type": "<class 'NoneType'>",
        "elements": 0,
        "errors": 1,
        "status": 500
    },
    "Response": {
        "data": null,
        "errors": [
            "B2ACCESS proxy not trusted by B2SAFE: excessive message size"
        ]
    }
}
