
# Welcome to `restangulask`

## The project

An attempt to mix Flask on both Frontend and Backend,
but with some extra help on client side from Angularjs.

## Start-up your project

Requested only the first time, after cloning from github:

```bash
# From the root directory of the project
./do YOUR_BLUEPRINT init
```

Subsequently, when you already have a running project
and you need to update the code, images and libraries:
```bash
./do YOUR_BLUEPRINT update
```

Note: all the specific configurations and files that could/should be edited can be found inside the `vanilla/` directory.

## Customize and run

Now the project is ready, and you can:

* Add [REST API resources](api.md) endpoints
* Add [Flask website pages]() **[TODO]**
* Or contributing by [developing new features](dev.md)

To test you simply need to run:

```bash
# Run Forest, run!
./do YOUR_BLUEPRINT restart
```

The command will bring up a Flask CMS mixed with Angularjs code,
and a REST API Flask service with user login.

## Scaffold

**WARNING: THIS HAS YET TO BE UPDATED**

```bash
├── jscode
│   └── base
│       └── script.js
├── jslibs
│   └── bower.json -> ../../angulask/jsdev/bower.json
├── pages
│   └── example.py
├── specs
│   └── init.json
└── templates
    ├── account
    │   ├── login.template.html
    │   └── register.template.html
    ├── customcss
    │   └── style.css
    └── framework
        ├── footer.html
        └── header.html
```
