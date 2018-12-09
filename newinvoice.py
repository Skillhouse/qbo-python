#!/usr/bin/env python 

import requests
import json
import sys
import hackerspace_utils as hu


authbag = hu.get_auth_bag()

Token = authbag['token'];

url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/invoice"

querystring = {"minorversion":"14"}

invoiceItem = {
    "value": 21,
    "name" : "Services",
}


InvoiceLine = {
    "Amount"     : 35.00,
    "DetailType" : "SalesItemLineDetail",
    "SalesItemLineDetail": { "ItemRef": invoiceItem  }
    }

invoice = { "CustomerRef": { "value": 58},
            "Line" : [
                InvoiceLine
                ]
            }

payload = json.dumps(invoice,indent=4,sort_keys=True)

print(payload)

headers = {
    'Accept': "application/json",
    'Content-Type': "application/json",
    'Authorization': "Bearer "+Token,
    'Cache-Control': "no-cache",
    }

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

print(response.text)









