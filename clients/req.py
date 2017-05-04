#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from beeprint import pp

TOKEN = ''

# Build request
r = requests.get(
    'http://localhost:8080/auth/profile',
    headers={'Authorization': 'Bearer ' + TOKEN}
)
out = r.json()

# Recover metadata
status = out['Meta']['status']
response = out.get('Response')
errors = response.get('errors') or []

# Decide on status
if len(errors) > 0:
    prefix = 'failed'
    if status == 401:
        prefix = 'unauthorized'
    print(prefix.capitalize() + ':')
    for error in response['errors']:
        print(error)
else:
    pp(response['data'])
