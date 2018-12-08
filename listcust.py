#!/usr/bin/env python 

import requests
import json
import hackerspace_utils as hu

authbag = hu.get_auth_bag()


url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/query"

querystring = {"minorversion":"14"}

payload="select * from Customer startposition 1 maxresults 30"

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

# print(json.dumps(resj,sort_keys=True,indent=4))


customers = resj['QueryResponse']['Customer']

#print(json.dumps(customers[0],indent=4))

distillate = { x['Id']:
               {
                   'id'    : x['Id'],
                   'email' : x['PrimaryEmailAddr']['Address'],
                   'DisplayName':x['DisplayName'],
                   'Notes': x['Notes'] if 'Notes' in x else "[no notes]" ,
                   'stripe': "",
#                   'QBOid': x['QBO ID']
               }
               for x in customers }

# print (json.dumps(distillate,sort_keys=True,indent=4))

# import pdb; pdb.set_trace()
# print ( ("{DisplayName}".format(**x) for x in distillate.values

print( "\n".join(["{id},{stripe},{email},{DisplayName}".format(**item) for item in distillate.values()  ]))




