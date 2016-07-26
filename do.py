# -*- coding: utf-8 -*-

import argparse
import os
import sys

from do_actions import InvalidArgument, NotImplementedAction
try:
    from vanilla.do_actions import CustomActions as ImplementedActions
    print("\nYou are using a custom implementation for actions")
except Exception as e:
    from do_actions import ImplementedActions
    print("\nYou are using the base implementation for actions")

INFO = "\033[1;32mINFO\033[1;0m"
WARNING = "\033[1;33mWARNING\033[1;0m"
ERROR = "\033[1;31mERROR\033[1;0m"


def myprint(level, message):
    print("%s: %s" % (level, message))


def list_all_projects():
    myprint(
        INFO, "List of available projects as found in **%s**" % CONTAINER_DIR)
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
    raise NotImplementedAction(
        "Print list of service from %s and exit" % yaml_file)


# Configuration

CONTAINER_DIR = "containers/custom"
BASE_YAML = "containers.yml"


# ############################################ #


# Arguments definition
parser = argparse.ArgumentParser(
    prog='do',
    description='Do things on this project'
)

parser.add_argument('--project', type=str, metavar='p',
                    help='Current project')
parser.add_argument('--mode', type=str, metavar='m',
                    help='Mode to be executed')
parser.add_argument('--list', action='store_true',
                    help='Docker compose service')
parser.add_argument('--action', type=str, metavar='a',
                    help='Desired action')
parser.add_argument('--service', type=str, metavar='s',
                    help='Docker compose service')
parser.add_argument('--workers', type=int, metavar='w',
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


# Implemented actions are automatically parsed by the ImplementedActions class
# all do_something methods are interpreted as 'something' actions
actions = []
for x in sorted(dir(ImplementedActions)):
    if x.startswith("do_"):
        actions.append(x[3:])

try:
    # List of available projects, when a project is not specified
    # Projects are directories into the CONTAINER_DIR
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
    command_prefix = "-f %s -f %s" % (base_yaml_path, mode_path)

    try:
        import inspect
        func = getattr(ImplementedActions, 'do_%s' % action)
        argspec = inspect.getargspec(func)
        func_args = []
        for a in argspec.args:
            if a == 'command':
                func_args.append(command_prefix)
            if a == 'project':
                func_args.append(project)
            if a == 'mode':
                func_args.append(mode)
            if a == 'action':
                func_args.append(action)
            if a == 'service':
                func_args.append(service)
            if a == 'num':
                func_args.append(num_workers)
            if a == 'arguments':
                func_args.append(extra_arguments)

        func(*func_args)

    except AttributeError as e:
        raise InvalidArgument('Method do_%s() not found' % action)

except InvalidArgument as e:
    myprint(ERROR, str(e))
    sys.exit(1)
except NotImplementedAction as e:
    myprint(WARNING, "NOT IMPLEMENTED: %s " % e)
    sys.exit(1)
