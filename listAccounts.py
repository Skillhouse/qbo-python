#!/usr/bin/env python 

import requests
import json
import hackerspace_utils as hu

authbag = hu.get_auth_bag()


url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/query"

querystring = {"minorversion":"14"}

payload="select * from Account startposition 1 maxresults 1000"

Token = authbag['token'];

headers = {
    'Accept': "application/json",
    'Content-Type': "application/text",
    'Authorization': "Bearer "+Token,
    'Cache-Control': "no-cache",
}

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

resj = json.loads(response.text);

# import pdb; pdb.set_trace()

if("Fault" in resj):
    print(json.dumps(resj,sort_keys=True,indent=4))
    raise(Exception("Failed transaction.."))

#print(json.dumps(resj,sort_keys=True,indent=4))


accounts = resj['QueryResponse']['Account']

distillate = { x['Id']:
               {
                   'id'    : x['Id'],
                   'name'  : x['Name'],
                   'type'  : x['AccountType'],
               }
               for x in accounts }



# print (json.dumps(distillate,sort_keys=True,indent=4))
# print ( ("{DisplayName}".format(**x) for x in distillate.values

print( "\n".join("{id},{type},{name}".format(**item)+"\n" for item in distillate.values()))



