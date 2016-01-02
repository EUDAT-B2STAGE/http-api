
# Configuration

All the API configuration variables are available in a file called
[`confs/config.py`](https://github.com/pdonorio/rest-mock/blob/master/confs/config.py#L11).

## Command line arguments

The app can be executed launching the `run.py` file found in the root of the project.

## What you should modify after a fork

Setup what will be the admin user and where the sqllite should be located:
```python
USER = 'user@nomail.org'
PWD = 'test'
SQLLITE_DBFILE = 'latest.db'
```

Set the following to true and run the server to clean everything
and restart from scratch.
```python
REMOVE_DATA_AT_INIT_TIME = False
```

## Other options

Take a look at all the variables.

You can add all the configurations for the existing plugins,
here's a list of links to see them all:

* [Flask](http://flask.pocoo.org/docs/0.10/config/#builtin-configuration-values)
* [Flask-sqlalchemy](http://flask-sqlalchemy.pocoo.org/2.1/config/#configuration-keys)
* [Flask-Security](https://pythonhosted.org/Flask-Security/configuration.html)

For example:

* you could use Mysql/Postgres relational db instead of
the development sqllite file db provided.


