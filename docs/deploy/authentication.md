
# Authentication mechanisms

Before deploying in production your B2STAGE HTTP-API server you should evaluate which mechanisms suites your use case for authentication.

There are two main available options:
1. a **local** authentication based on the accounts registered in the B2SAFE connected server
2. a **global** EUDAT authentication relying on the B2ACCESS service


## B2ACCESS 

[B2ACCESS](https://eudat.eu/b2access) is the service that holds the official/global EUDAT authentication across the whole international infrastructure.

Your application must be registered as a client for the B2ACCESS OAUTH protocol. If you don't have such registration you can proceed with the following steps:

- Go to the B2ACCESS server instance you need to refer. There are three instances available at the moment of writing you can choose:
    1. The official [production instance](https://b2access.eudat.eu/home/)
    2. The [integration instance](https://b2access-integration.fz-juelich.de/home/)
    3. Finally the [development instance](https://unity.eudat-aai.fz-juelich.de/home/)
- Click on the `register a new account` link on the website
- Choose the `Oauth 2.0 Client Registration Form`
- As `OAuth client return URL` indicate `https://YOUR_SERVER/auth/authorize`
- Once you receive your credentials you have to apply them in the [project_configuration.yaml](https://github.com/EUDAT-B2STAGE/http-api/blob/1.0.2/projects/b2stage/project_configuration.yaml) dedicated variables (with the `B2ACCESS_` prefix).

Once you start the B2STAGE server with the two variables `B2ACCESS_ACCOUNT` and `B2ACCESS_SECRET` set, the related endpoints will be activated (you may double-check this inside your `/api/specs` JSON content).

Please read also how the authentication works for a user [here](/docs/user/authentication.md)

### Current issues

**Warning**: there is an ongoing issue between `B2SAFE` and `B2ACCESS` on their trust of chain based on `X509` certificates. Only the development instance of B2ACCESS is known to work correctly at the time of writing.

For more informations please ask in the dedicated [chat channel](https://gitter.im/EUDAT-B2STAGE/http-api).

<!--
This means that with the HTTP API running the B2ACCESS authentication mechanism you can correctly obtain a token to authenticate, but this token would not be accepted from B2SAFE.
The two teams have are currently working off a solution. A few options are being evaluated and more informations will be provided as soon as possible in the [chat channel](https://gitter.im/EUDAT-B2STAGE/http-api).
-->

## B2SAFE

[B2SAFE](https://www.eudat.eu/b2safe) offers through its `iRODS` server a local management of users which is not related to the EUDAT centralized accounting.

Once you start the B2STAGE server without setting the two variables `B2ACCESS_ACCOUNT` and `B2ACCESS_SECRET` (which is the **`default`** as for the current open issues), the related endpoints will be activated (you may double-check this inside your `/api/specs` JSON content).

Please read also how the authentication works for a user [here](/docs/user/authentication_b2safe.md).

