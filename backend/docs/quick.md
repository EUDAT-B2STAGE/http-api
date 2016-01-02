
# Getting started

### Prerequisites

Install docker and docker-compose. For example:

```
# Install docker
curl -sSL https://get.docker.com/ | sh
# Install docker-compose
pip install -U docker-compose
```

### How to run

```
$ git clone https://github.com/pdonorio/rest-mock.git
$ cd rest-mock
$ docker-compose up
```

### How to test

You may test via command line with **wget** or **curl**.

```
curl -v http://localhost:8081/api/foo
```

To write a client with python i would suggest using `requests` library.
To write a javascript client take a look at `Angularjs` and `Restangular` (install them with `bower`, it's easier).

My favorite API test app is [httpie](http://httpie.org), which is written in python too.
