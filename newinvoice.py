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
    'User-Agent': "QBOV3-OAuth2-Postman-Collection",
    'Accept': "application/json",
    'Content-Type': "application/json",
    'Authorization': "Bearer "+Token,
    'Cache-Control': "no-cache",
    'Postman-Token': "93f5ea65-5a55-496d-87ef-4b1e9c5859ec"
    }

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

print(response.text)









