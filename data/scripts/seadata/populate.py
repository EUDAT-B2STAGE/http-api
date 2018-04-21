# -*- coding: utf-8 -*-

# import requests
import sys
import json
from utilities import apiclient

LOG_LEVEL = 'info'  # or 'debug', 'verbose', 'very_verbose'
log = apiclient.setup_logger(__name__, level_name=LOG_LEVEL)

#####################
# records_file = 'json_records.txt'
# protocol = 'https'
# server = 'seadata.cineca.it'
# username = 'paolobeta'
# password = 'thisisalongerpassword'

records_file = 'json_records.txt'
# records_file = 'json_records.txt.short'
protocol = 'http'
server = 'localhost:8080'
username = 'paolobeta'
password = 'thisisalongerpassword'

#####################
counter = 0
base_url = '%s://%s' % (protocol, server)
batch_id = 'initial_loading_01'
endpoint = '/api/ingestion'
prefix = 'm_0/d_1/'
# prefix = 'm_0/d_0/'

#####################
# 0. authenticate
if len(sys.argv) > 1:
    token = sys.argv[1]
else:
    token, _ = apiclient.login(base_url, username, password)
log.info("TOKEN:\n%s", token)

# #####################
# # 1. POST create batch
# out = apiclient.call(
#     base_url, endpoint=endpoint, method='post',
#     token=token, payload={'batch_id': batch_id},
# )
# log.info("Batch: %s", out)

#####################
move_json = {
    "request_id": 1975,
    "edmo_code": 486,
    "datetime": "20180312T16:03:52",
    "version": "1",
    "api_function": "move_to_production",
    "test_mode": "true",
    "parameters": {
        "batch_number": batch_id,
        "pids": []
    }
}

#####################
fp = open(records_file)
myjson = json.load(fp)

# test = 'test.empty.txt'
# myjson = [test]
# for element in myjson:
#     filepath = element

for element in myjson.get('parameters', {}).get('pids', []):
    filepath = element.get('temp_id').replace('export/', '')
    if not filepath.startswith(prefix):
        continue

    print(filepath)
    from utilities import path
    move_json['parameters']['pids'].append({
        "temp_id": path.last_part(filepath),
        "cdi_n_code": "2449338",
        "format_n_code": "3994177",
        "data_format_l24": "ODV",
        "version": "1"
    })
    # print(element)

    # counter += 1
    # if counter > 1:
    #     log.pp(move_json)
    #     break

    # # 2. PUT file in batch
    # pass

# log.pp(move_json)
# exit(0)

#####################
# 3. Move files into production
# POST /api/ingestion/<batch_id>/approve
# about ~ 25 minutes for iput + PID on 1000 elements
out = apiclient.call(
    base_url,
    endpoint=endpoint + '/%s/approve' % batch_id, method='post',
    token=token, payload=move_json, timeout=99999,
)

pids = []
if isinstance(out, dict):
    for element in out.get('parameters', []):
        pids.append({element.get('temp_id'): element.get('pid')})
    log.pp(pids)
    with open('output.json', 'w') as fp:
        json.dump(pids, fp)

log.warning('done')
