#!/usr/bin/env python 

import requests
import json
import hackerspace_utils as hu

authbag = hu.get_auth_bag()


url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/query"

querystring = {"minorversion":"14"}

payload="select * from invoice startposition 1 maxresults 5"

Token = authbag['token'];

headers = {
    'Accept': "application/json",
    'Content-Type': "application/text",
    'Authorization': "Bearer "+Token,
    'Cache-Control': "no-cache",
}

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)


resj = json.loads(response.text);
qresult = resj['QueryResponse']
invoices = qresult['Invoice']

# import pdb; pdb.set_trace()

distillate = { inv['Id']:
               {
                   'custid':inv['CustomerRef']['value'],
                   'custname':inv['CustomerRef']['name'],
                   'TxnDate':inv['TxnDate'],
                   'Amount':inv['TotalAmt'],
               }
               for inv in invoices }

print (json.dumps(distillate,sort_keys=True,indent=4))








