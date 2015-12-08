
# Welcome to `restangulask`

## The project

An attempt to mix Flask on both Frontend and Backend

but with some extra help on client side from Angularjs

## Init the project

Requested only the first time and after code updates

```bash
# From the root directory of the project
./boot.sh bower
```

Note: all the specific configurations and files that could/should be edited can be found inside the `vanilla/` directory.

## How to run

```bash
# From the root directory of the project
./boot.sh
```

## Install a new package via bower

```bash
# From the root directory of the project
./boot.sh bower PACKAGE_NAME
```

## Scaffold

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
