
# Updates

Once you have installed and deployed your HTTP API server correctly the main task to keep track of is *maintenance*.

Since development is on going there will be two possible actions:

- Updates/patches on the currently installed release
- Upgrade to a new release

## Check for updates

To be continued...


## Update

To be continued...

```bash
$ rapydo update --rebuild && rapydo restart
```

## Upgrade

To be continued...

```bash
$ rapydo upgrade 

[INFO    controller.app:1585] Current release: 1.0.2
[WARNING controller.app:1510] List of available releases:

 - 0.5.1 beta (rapydo None) [released]
 - 0.5.2 beta (rapydo None) [discontinued]
 - 0.6.0 RC1 (rapydo 0.5.3) [released]
 - 0.6.1 RC2 (rapydo 0.5.4) [released]
 - 1.0.0 stable (rapydo 0.6.0) [released]
 - 1.0.1 patch (rapydo 0.6.1) [released]
 - 1.0.2 patch (rapydo 0.6.1) [released] *installed*
 - 1.0.3 stable (rapydo 0.6.2) [released]
 - 1.0.4 development (rapydo 0.6.3) [development]
```

