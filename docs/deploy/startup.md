
# Start-up the project


## 1. cloning 

To clone the working code:

```bash
$ VERSION=1.0.4 \
    && git clone https://github.com/EUDAT-B2STAGE/http-api.git \
    && cd http-api \
    && git checkout $VERSION  

# now you will have the current latest release
```


## 2. configure

Now that you have all necessary software installed, before launching services you should consider editing the main configuration:

[`projects/b2stage/project_configuration.yaml`](projects/b2stage/project_configuration.yaml)

Here you can change at least the basic passwords, or configure access to external service (e.g. your own instance of iRODS/B2SAFE) for production.


## 3. controller

The controller is what let you manage the project without much effort.
Here's what you need to use it:

```bash
# install and use the rapydo controller
$ data/scripts/prerequisites.sh 
# you have now the executable 'rapydo'
$ rapydo --version
# If you use a shell different from bash (e.g. zsh) 
# you can try also the short alias 'do'
$ do --help
```

NOTE: python install binaries in `/usr/local/bin`. If you are not the admin/`root` user then the virtual environment is created and you may find the binary in `$HOME/.local/bin`. Make sure that the right one of these paths is in your `$PATH` variable, otherwise you end up with `command not found`.


## 4. deploy initialization

Your current project needs to be initialized. This step is needed only the first time you use the cloned repository.

```bash
$ rapydo init
```

If you wish to __**manually upgrade**__:

```bash
VERSION="0.6.3"
git checkout $VERSION

# supposely the rapydo framework has been updated, so you need to check:
rm -rf submodules/*
data/scripts/prerequisites.sh
rapydo init

# update docker images with the new build templates in rapydo
# NOTE: select your mode based on the next paragraph
rapydo --mode YOURMODE build -r -f
```
