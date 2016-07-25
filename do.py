# -*- coding: utf-8 -*-

import argparse
import os
import sys

INFO = "\033[1;32mINFO\033[1;0m"
WARNING = "\033[1;33mWARNING\033[1;0m"
ERROR = "\033[1;31mERROR\033[1;0m"


def _exec(command):
    print ("\nCommand to be executed:\n\tdocker-compose %s\n\n" % command)


def myprint(level, message):
    print("%s: %s" % (level, message))


def list_all_projects():
    myprint(INFO, "List of available projects as found in **%s**" % CONTAINER_DIR)
    projects = os.listdir(CONTAINER_DIR)
    projects.sort()
    num = 0
    for p in projects:
        project_path = os.path.join(CONTAINER_DIR, p)
        if not os.path.isdir(project_path):
            continue
        myprint(INFO, "\t- %s" % p)
        num += 1

    if num == 0:
        myprint(WARNING, "\t- None")


def list_all_modes(project, project_path):
    myprint(INFO, "List of available modes in project **%s**" % project)

    modes = os.listdir(project_path)
    modes.sort()
    num = 0
    for m in modes:
        mode_path = os.path.join(project_path, m)
        if os.path.isdir(mode_path):
            continue
        if not m.endswith(".yml"):
            continue

        myprint(INFO, "\t- %s" % m[0:-4])
        num += 1

    if num == 0:
        myprint(WARNING, "\t- None")


def list_all_services(yaml_file):
    myprint(INFO, "Print list of service from %s and exit" % yaml_file)


class InvalidArgument(BaseException):
    pass


class NotImplemented(BaseException):
    pass


# Configuration

CONTAINER_DIR = "containers/custom"
BASE_YAML = "containers.yml"

actions = {
    "check", "init", "update", "bower", "start", "stop",
    "restart", "graceful", "logs", "remove", "clean",
    "command", "shell", "scale"
}

# ############################################ #


# Arguments definition
parser = argparse.ArgumentParser(
    prog='do',
    description='Do things on this project'
)

parser.add_argument('--project', type=str,
                    help='Current project')
parser.add_argument('--mode', type=str,
                    help='Mode to be executed')
parser.add_argument('--list', action='store_true',
                    help='Docker compose service')
parser.add_argument('--action', type=str,
                    help='Desired action')
parser.add_argument('--service', type=str,
                    help='Docker compose service')
parser.add_argument('--workers', type=int,
                    help='Number of celery workers to be executed')
parser.add_argument('extra_arguments',
                    help='Extra arguments for bower and command actions',
                    nargs='*')

# Reading input parameters
args = parser.parse_args()

args = vars(args)

project = args['project']
mode = args['mode']
list_services = args['list']
action = args['action']
service = args['service']
num_workers = args['workers']
extra_arguments = args['extra_arguments']

if extra_arguments is not None:
    extra_arguments = ' '.join(extra_arguments)

try:
    # List of available projects, when a project is not specified
    # Projects are directory into the CONTAINER_DIR
    if project is None:
        list_all_projects()
        sys.exit(0)

    project_path = os.path.join(CONTAINER_DIR, project)
    if not os.path.isdir(project_path):
        raise InvalidArgument("Project not found (%s)" % project_path)

    myprint(INFO, "You selected project: \t%s" % project)

    # List of available modes, when a mode is not specified
    # Modes are .yml files into the CONTAINER_DIR/project dir
    if mode is None:
        list_all_modes(project, project_path)
        sys.exit(0)

    # The specified mode doesn't exist
    mode_path = os.path.join(project_path, mode) + ".yml"
    if not os.path.isfile(mode_path):
        raise InvalidArgument("Mode not found (%s)" % mode_path)

    myprint(INFO, "You selected mode: \t%s" % mode)

    # List of available services obtained from the specified /project/mode.yml
    if list_services:
        list_all_services(mode_path)
        sys.exit(0)

    if action == 'scale':
        raise InvalidArgument(
            'Use parameter --workers instad of --action scale')

    if num_workers is not None:
        action = 'scale'

    if action is None or action not in actions:
        raise InvalidArgument(
            "You should specify a valid action.\n" +
            "Available actions:\n\t%s" % actions
        )

    if num_workers is not None:
        myprint(INFO, "You selected action: \t%s=%s" % (action, num_workers))
    elif extra_arguments is not None:
        myprint(INFO, "You selected action: \t%s %s" %
                (action, extra_arguments))
    else:
        myprint(INFO, "You selected action: \t%s" % action)

    base_yaml_path = os.path.join(CONTAINER_DIR, BASE_YAML)
    command = "-f %s -f %s" % (base_yaml_path, mode_path)

    def service_mandatory(service):
        if service is None:
            raise InvalidArgument(
                'Service parameters is mandatory for this action'
            )

    def service_incompatible(service):
        if service is not None:
            raise InvalidArgument(
                'Service parameter is incompatible with this action'
            )

    def do_check(project, action, service):
        service_incompatible(service)
        raise NotImplemented(
            'verify if the %s blueprint is well-configured' % project
        )

    def do_init(command, action, service):
        service_incompatible(service)
        raise NotImplemented(
            'init the %s blueprint (in old do command)' % project
        )

    def do_update(command, action, service):
        service_incompatible(service)

        _exec("%s %s" % (command, action))

    def do_start(command, action, service):
        service_mandatory(service)
        _exec("%s %s %s" % (command, action, service))

    def do_stop(command, action, service):
        service_mandatory(service)
        _exec("%s %s %s" % (command, action, service))

    def do_restart(command, action, service,):
        service_mandatory(service)
        _exec("%s %s %s" % (command, action, service))

    def do_graceful(command, action, service):
        service_mandatory(service)
        _exec("%s %s %s" % (command, action, service))

    def do_scale(command, action, service, num):
        service_mandatory(service)
        _exec("%s %s %s=%s" % (command, action, service, num))

    def do_logs(command, action, service):
        if service is None:
            _exec("%s %s" % (command, action))
        else:
            _exec("%s %s %s" % (command, action, service))

    # service is required or not for this action?
    def do_remove(command, action, service):
        service_mandatory(service)
        _exec("%s %s %s" % (command, action, service))

    # service is required or not for this action?
    def do_clean(command, action, service):
        service_mandatory(service)
        _exec("%s %s %s" % (command, action, service))

    def do_command(command, action, service, arguments):
        service_mandatory(service)
        if len(arguments) == 0:
            raise InvalidArgument('Missing arguments for command action')

        _exec("%s exec %s %s" % (command, service, arguments))

    def do_shell(command, action, service):
        service_mandatory(service)
        do_command(command, action, service, arguments='bash')

    def do_bower(command, action, service, arguments):
        service_incompatible(service)
        if len(arguments) == 0:
            raise InvalidArgument('Missing arguments for bower action')

        do_command(command, action, service='bower', arguments=arguments)

    if action == 'check':
        do_check(project, action, service)
    elif action == 'init':
        do_init(project, action, service)
    elif action == 'update':
        do_update(command, action, service)
    elif action == 'start':
        do_start(command, action, service)
    elif action == 'stop':
        do_stop(command, action, service)
    elif action == 'restart':
        do_restart(command, action, service)
    elif action == 'graceful':
        do_graceful(command, action, service)
    elif action == 'scale':
        do_scale(command, action, service, num_workers)
    elif action == 'logs':
        do_logs(command, action, service)
    elif action == 'shell':
        do_shell(command, action, service)
    elif action == 'remove':
        do_remove(command, action, service)
    elif action == 'clean':
        do_clean(command, action, service)
    elif action == 'bower':
        do_bower(command, action, service, extra_arguments)
    elif action == 'command':
        do_command(command, action, service, extra_arguments)

except InvalidArgument as e:
    myprint(ERROR, str(e))
    sys.exit(1)
except NotImplemented as e:
    myprint(WARNING, "NOT IMPLEMENTED: %s " % e)
    sys.exit(1)
