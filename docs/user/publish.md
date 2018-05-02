
# Publish data

Data available on `B2SAFE` can be shared to non-authenticated users.

To allow such operations we are testing a new experimental feature. To mymic access for any user inside the iRODS technology behind B2SAFE [the irods *anonymous* user](https://docs.irods.org/4.2.0/system_overview/users_and_permissions/#tickets-guest-access) is the chosen implementation; this is the equivalent of a *guest* user mechanism.

## The workflow

- You have some data object registered in `B2SAFE` on some `ipath`
- You can check if your data object is publish with a call to `GET` method of `/api/publish/<ipath>` 
- You can publish your data object with a call to `PUT` method of `/api/publish/<ipath>` 
- You can unpublish your data object with a call to `DELETE` method of `/api/publish/<ipath>` 

When a data object is published to any guest user access, it's accessible via browser to the URL `/api/public/<ipath>`.

## Caveats

NOTE: This feature is not enabled by default.

This feature depends on the variable `IRODS_ANONYMOUS` in the project configuration file. If the variable is set to `1` then the anonymous user is expected to be found in the `B2SAFE` instance. A check at startup is made to verify the condition.

To create the anonymous user on an irods instance you would require these commands:

```bash
imkdir /$IRODS_ZONE/home/anonymous
ichmod write anonymous /$IRODS_ZONE/home/anonymous
ichmod read anonymous /$IRODS_ZONE/home/public
```




