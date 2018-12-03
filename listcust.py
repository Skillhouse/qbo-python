#!/usr/bin/env python 

import requests
import json
import hackerspace_utils as hu

authbag = hu.get_auth_bag()


url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/query"

querystring = {"minorversion":"14"}

payload="select * from Customer startposition 1 maxresults 5"

Token = authbag['token'];

headers = {
    'User-Agent': "QBOV3-OAuth2-Postman-Collection",
    'Accept': "application/json",
    'Content-Type': "application/text",
    'Authorization': "Bearer "+Token,
    'Cache-Control': "no-cache",
}

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)


resj = json.loads(response.text);
customers = resj['QueryResponse']['Customer']

print(json.dumps(customers[0],indent=4))

distillate = { x['Id']:
               {
                   'email' : x['PrimaryEmailAddr']['Address'],
                   'DisplayName':x['DisplayName'],
               }
               for x in customers }

print (json.dumps(distillate,sort_keys=True,indent=4))






