# -*- coding: utf-8 -*-

import argparse
import os
import sys
import logging


INFO = "\033[1;32mINFO\033[1;0m"
WARNING = "\033[1;33mWARNING\033[1;0m"
ERROR = "\033[1;31mERROR\033[1;0m"

"""
from compose.cli.main import TopLevelCommand
from compose.cli.command import project_from_options
import compose.cli.errors as errors
from compose.cli.docopt_command import DocoptDispatcher


def compose_com(cli_options):

    dispatcher = DocoptDispatcher(
        TopLevelCommand,
        {'options_first': True, 'version': '1.7.1'})

    options, handler, command_options = dispatcher.parse(cli_options)

    # print("TEST", options, handler, command_options)
    # exit(1)

    project = project_from_options('.', options)
    command = TopLevelCommand(project)

    with errors.handle_connection_errors(project.client):
        out = handler(command, command_options)
        print("Launched command, with output:\n", out)
    return out


#############################

# Detached command doesn't return any output
# compose_com(['up', '-d', 'graphdb'])
compose_com(['ps'])
"""

CONTAINER_DIR = "containers/custom"
BASE_YAML = "containers.yml"


def _exec(command):
    print ("\nCommand to be executed:\n\tdocker-compose %s\n\n" % command)

def myprint(level, message):
	print("%s: %s" % (level, message))


parser = argparse.ArgumentParser(
    prog='do',
    description='Do things on this project'
)

parser.add_argument('--project', type=str,
                    help='current project')
parser.add_argument('--mode', type=str,
                    help='mode to be executed')
parser.add_argument('--list', action='store_true',
                    help='docker compose service')
parser.add_argument('--action', type=str,
                    help='desired action')
parser.add_argument('--service', type=str,
                    help='docker compose service')
parser.add_argument('--workers', type=int,
                    help='number of celery workers to be executed')

# MYPROJECT MODE ACTION [SERVICE] [NUMBER_OF_WORKERS]

args = parser.parse_args()

args = vars(args)

project = args['project']
mode = args['mode']
list_services = args['list']
action = args['action']
service = args['service']
num_workers = args['workers']

if project is None:
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
    sys.exit(1)


project_path = os.path.join(CONTAINER_DIR, project)
if not os.path.isdir(project_path):
    myprint(ERROR, "Project not found (%s)" % project_path)
    sys.exit(1)
	    
myprint(INFO, "You selected project: %s" % project)

if mode is None:
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
    sys.exit(1)


mode_path = os.path.join(project_path, mode) + ".yml"

if not os.path.isfile(mode_path):
    myprint(ERROR, "Mode not found (%s)" % mode_path)
    sys.exit(1)

myprint(INFO, "You selected mode: %s" % mode)

if list_services:
	myprint(INFO, "Print list of service from %s and exit" % mode_path)
	sys.exit(0)

if action is None:
	myprint(ERROR, "You should specify an action. Available action are:")
	myprint(ERROR, "start, stop, restart, graceful, logs, scale, remove, clean, command, open shell")

if service is None and num_workers is not None:
    myprint(
        ERROR,
        "No service specification found, num worker option cannot be applied"
    )
    sys.exit(1)


base_yaml_path = os.path.join(CONTAINER_DIR, BASE_YAML)
command = "-f %s -f %s %s" % (base_yaml_path, mode_path, action)

if service is not None:
    if num_workers is not None:
    	command = "%s=%s" % (command, service, num_workers)
    else:
        command = "%s %s" % (command, service)

_exec(command)
