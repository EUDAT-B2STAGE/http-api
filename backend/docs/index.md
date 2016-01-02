
# An introduction

## Project motivations

I have been working off Flask for a quite time now; and since Python is a language about being better (also a [better you](http://pile.wf/about-being-better/)) i am trying to rewrite my base work in a cleaner way.

### Should i use this?

I think this repo would be usefull to fork if you are planning to write a project where you know you want to use Flask as REST API endpoint somewhere.

1. First you could write mocks for your interface to test
2. Then implement them with whatever you want as background middleware
    <small> e.g. FS (irods), graphDB (neo4j), whatever </small>

### Ideal scheduling

* A scratch mock as generic as possible
* Add as soon as possible few design patterns: logs, configuration, etc.
* Fork this repo for an advanced and generic REST API
* Add cool stuff (admin dashboard, app DB ORM, queues, workers, etc.)
    *Note: i am up to here*
* But **KEEP IT AS GENERIC AS POSSIBLE**...!


### What it will be based on

* Flask (*obviously*)
* Jinja2
* Flask Cors
* Flask Restful plugin (even if evaluating *Flask Classy*, also)
* Flask Security
    Simple RBAC + OAuth tokens + encryption +
    user registration + Login + Principal
* Flask Admin interface

*Still to be added:*

* Flask-JWT
* Plumbum
* Tracestack
* Mail
* Flask Cache
* Flask Uploads
* Alembic? migrations for SQLalchemy

---

## Creator(s)

[Paolo D'Onorio De Meo](https://twitter.com/paolodonorio/)

## Copyright and license

Code and documentation copyright: `Paolo D'Onorio De Meo @2015`.

Code released under the [MIT license](LICENSE).
