# Keeping track of important modifications while developing

## Changes that break compatibility

### Docker volume prefix

```2016 \ 03 \ 14 ```


Inside the madness of docker volume random names,
i found my self getting crazy to remove only the unwanted.

To make things easier, since we don't have yet a system for labeling the volumes, i will give a fixed prefix to volumes belonging to the same project.

In this case you are all encouraged to use the prefix `restangulask_` for any extra volume you come to use inside your custom `YAML` file for `docker-compose`.

I will write the upcoming code from now on taking this behavior from granted.

### Other?

To do
