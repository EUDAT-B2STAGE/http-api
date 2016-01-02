# -*- coding: utf-8 -*-

""" Client for api """

import requests
import simplejson as json

NODE = 'api'
PORT = 5000
USER = 'user@nomail.org'
PW = 'test'

URL = 'http://%s:%s' % (NODE, PORT)
LOGIN_URL = URL + '/login'
HEADERS = {'content-type': 'application/json'}
payload = {'email': USER, 'password': PW}

# http://mandarvaze.github.io/2015/01/token-auth-with-flask-security.html
r = requests.post(LOGIN_URL, data=json.dumps(payload), headers=HEADERS)

###################
print(r, r.url)
print("RESPONSE:")
try:
    print(r.json())
except:
    print(r.text)
