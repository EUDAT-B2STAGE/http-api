
# Deployment pre-requisites

In order to deploy this project you need to install the `RAPyDO controller` and use it to startup the services on a `Docker` environment with containers.

The following instruction are based on the hyphotesis that you will work on a `UNIX`-based OS. Any `Linux` distributions (Ubuntu, CentOS, Fedora, etc.) or any version of `Mac OSX` are supported.

Command line examples were heavily tested on `bash` terminal (version `4.4.0`, but all versions `4.x` and `3.x` should work). Also keep in mind that installing tools into your machine is suggested through your preferred OS package manager (e.g. `apt`, `yum`, `brew`, etc.).


## Base tools

### Python 3

- The `python 3.4+` interpreter installed together with its main package manager `pip3`.

Most of distributions comes bundled with `python 2.7+`, which is not suitable for our project. Once again use a package manager if possible. 
For example:

- in `Ubuntu` you would base your request on `apt` commands, e.g.
```bash
sudo apt-get update && sudo apt-get install python3-pip
```

- in CentOS you would need to use `yum`, e.g.
```bash
sudo yum -y update  
# warning: this command above can install a lot of packages
# if your system is not quite up-to-date

# install python 3.6 (latest stable Python) and the pip package manager
sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
sudo yum -y install python36u python36u-pip
sudo ln -s /usr/bin/pip3.6 /usr/bin/pip3
```

##  GIT

Most of UNIX distributions have the `git` command line client already installed. If that is not that case then refer to the [official documentation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

Examples with OS package manager:
```bash
# ubuntu
sudo apt-get update && sudo apt-get install -y git
# centos
sudo yum -y install git
```

## Containers environment

### docker engine

Please *NOTE*: if you are using `Red Hat` (RHEL) as Operating System, Docker is supported [only in the enterprise edition](https://docs.docker.com/install/linux/docker-ee/rhel/#prerequisites).

---

To install docker on a unix terminal in a very easy and quick way you can try the [get docker script](https://get.docker.com), e.g.:

```
# Install docker
$ curl -fsSL get.docker.com -o get-docker.sh
$ sudo sh get-docker.sh

# add a user to launch docker containers
sudo usermod -aG docker YOUR_USER_NAME

# then make sure your docke engine is running, e.g. in CentOS:
sudo systemctl start docker
# in Ubuntu it should be already running
```

For Mac and Windows users dedicated applications were written: 

- [Docker for Mac](https://www.docker.com/docker-mac)  
- [Docker for Windows](https://www.docker.com/docker-windows)

As alternative, the best way to get Docker ecosystem/tools working
is by using their existing [toolbox](https://www.docker.com/toolbox).

### docker compose

`Compose` is a tool for docker written in Python. See the [official instructions](https://docs.docker.com/compose/install/) to install it.

If you installed `pip3` from above you can also try with:
```bash
$ sudo -H pip3 install --upgrade docker-compose
```

NOTE: compose comes already bundled within the docker toolbox.


## Production instance


The B2STAGE HTTP API server acts as a proxy interface to a real B2SAFE instance. Having B2SAFE *already running in production* and correctly set up would be a requisite if you want to deploy our project on top of it.

To understand more you can refer to the [official B2SAFE documentation](https://github.com/EUDAT-B2SAFE/B2SAFE-core/blob/master/install.txt#L1).
