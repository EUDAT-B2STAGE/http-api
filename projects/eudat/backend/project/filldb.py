# -*- coding: utf-8 -*-

# from rapydo.utils.basher import BashCommands
import os
from pymongo import MongoClient
from rapydo.utils.logs import get_logger

log = get_logger(__name__)

# bash = BashCommands()
# output = bash.execute_command("ls", ['-l', 'eudat'])
# log.debug(output)

client = MongoClient(
    os.environ.get('MONGO_HOST'),
    int(os.environ.get('MONGO_PORT'))
)

print(client)
