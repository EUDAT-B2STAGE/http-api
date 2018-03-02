"""
Ingestion enable and file upload (RM)
"""

import requests

server_uri = 'seadata.cineca.it'
token = 'YOUR TOKEN HERE'
file_path = '/path/to/your/file'
batch_id = 'test_python'
headers = {"Authorization": "Bearer %s" % token}

with open(file_path, 'rb') as f:

    url = 'https://%s/api/ingestion' % server_uri

    # enable
    r = requests.post(url, params={'batch_id': batch_id}, headers=headers)
    if r.status_code > 299:
        print("Failed: status %s" % r.status_code)
    else:
        print("Success", r.json())

    # upload
    headers["Content-Type"] = "application/octet-stream"
    r = requests.put('%s/%s' % (url, batch_id), data=f, headers=headers)
    if r.status_code > 299:
        print("Failed: status %s" % r.status_code)
    else:
        print("Success", r.json())
