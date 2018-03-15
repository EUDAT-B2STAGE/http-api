
# Deployment pre-requisites

In order to deploy this project you need to install the `RAPyDO controller` and use it to startup the services on a `Docker` environment with containers.

The following instruction are based on the hyphotesis that you will work on a `UNIX`-based OS. Any `Linux` distributions (Ubuntu, CentOS, Fedora, etc.) or any version of `Mac OSX` will do. Command line examples were heavily tested on `bash` terminal (version `4.4.0`, but also version `3.x` should work).

Please note that for installing tools into your machine the suggested option is through your preferred OS package manager (e.g. `apt`, `yum`, `brew`, etc.).


## Base tools

- The `git` client. 
 
Most of UNIX distributions have it already installed. If that is not that case then refer to the [official documentation]()

- The `python 3.4+` interpreter installed together with its main package manager `pip3`.

Most of distributions comes bundled with `python 2.7+`, which is not suitable for our project. Once again use a package manager, for example in ubuntu you would run:

```bash
$ apt-get update && apt-get install python3-pip
```


## Containers environment

### docker engine

Please *NOTE*: if you are using `Red Hat` (RHEL) as Operatin System, Docker is supported [only in the enterprise edition](https://docs.docker.com/install/linux/docker-ee/rhel/#prerequisites).

---

To install docker on a unix terminal you may use the [get docker script](https://get.docker.com):

```
# Install docker
$ curl -fsSL get.docker.com -o get-docker.sh
$ sh get-docker.sh
```

For Mac and Windows users dedicated applications were written: 

- [Docker for Mac](https://www.docker.com/docker-mac)  
- [Docker for Windows](https://www.docker.com/docker-windows)

As alternative, the best way to get Docker ALL tools working
is by using their [toolbox](https://www.docker.com/toolbox).

### docker compose

`Compose` is a tool for docker written in Python. See the [official instructions](https://docs.docker.com/compose/install/) to install it.

NOTE: compose comes bundled with the toolbox.
