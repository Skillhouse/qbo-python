#!/usr/bin/env python 

import requests
import json
import hackerspace_utils as hu
from urllib.parse import urlencode
import base64


authbag = hu.get_auth_bag()

querystring = {"minorversion":"14"}


Token = authbag['token'];

def stringToBase64(s):
    return base64.b64encode(bytes(s, 'utf-8')).decode()

headers = {
    'Accept': "application/json",
    'Content-Type': "application/x-www-form-urlencoded",
    'Authorization':  'Basic ' + stringToBase64(authbag['client'] + ':' + authbag['secret']),
    'Cache-Control': "no-cache",
}

url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

payload = {
    'grant_type'    : 'refresh_token',
    'refresh_token' : authbag['refresh_token'],
    }

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

resj = json.loads(response.text);


print(response)

print(response.text)

print(json.dumps(resj,indent=4,sort_keys=True))

import pdb; pdb.set_trace()






