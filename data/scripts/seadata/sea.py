
###############################################
# count current batch import

import os
import json
# from datetime import datetime
from glob import glob as find
from plumbum.cmd import imeta, grep

pid_prefix = '21.T12995'
irods_path = "/sdcCineca/cloud"
main_path = '/mnt/data1/irods/Vault/cloud'
prefix_batches = 'import01june_rabbithole_500000_'
os.chdir(main_path)

files = find("./%s*/**.txt" % prefix_batches)
# print(datetime.now(), len(files))

###############
# Obtain pids (requires 'plumbum')
counter = 0
data = {}
for file in files:
    counter += 1
    pieces = file.split('/')
    filename = pieces.pop()
    batch = pieces.pop()
    ipath = os.path.join(irods_path, batch, filename)
    chain = imeta['ls', '-d', ipath] | grep[pid_prefix]
    try:
        out = chain()
    except Exception as e:
        print('failed: %s [%s]' % (filename, batch))
        continue
    pid = out.split(' ')[1].rstrip()
    # print(filename, pid.encode('ascii'))
    data[filename] = pid.encode('ascii')

    if counter % 100 == 0:
        print("Found: %s" % counter)
        # break
    if counter % 10000 == 0:
        print("saving what we have so far")
        with open('/tmp/test.json', 'w') as fh:
            json.dump(data, fh)

with open('/tmp/test.json', 'w') as fh:
    json.dump(data, fh)

"""
(datetime.datetime(2018, 6, 1, 23, 36, 56, 304232), 37738)
(datetime.datetime(2018, 6, 2, 6, 57, 35, 644743), 82849)
(datetime.datetime(2018, 6, 2, 10, 12, 52, 812827), 103112)
(datetime.datetime(2018, 6, 3, 10, 33, 53, 584727), 254153)
"""

# ###############################################
# # Graceful shutdown of celery worker(s)

# """
# http://docs.celeryproject.org/en/latest/userguide/workers.html#stopping-the-worker
# """

# from restapi.flask_ext import get_debug_instance
# from restapi.flask_ext.flask_celery import CeleryExt
# obj = get_debug_instance(CeleryExt)
# workers = obj.control.inspect()
# workers.active().keys()
# w = list(workers.active().keys())

# # https://stackoverflow.com/a/41885106
# # celery.control.broadcast('shutdown', destination=[<celery_worker_name>])

# for element in w:
#     print(element)  # celery@worker-25d6b959aa91 ?

