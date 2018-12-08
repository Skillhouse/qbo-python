

import requests
import json
import hackerspace_utils as hu
import sys


authbag = hu.get_auth_bag()
Token = authbag['token'];


custfields = {
    'name'    :  lambda d,v: d.update({'DisplayName':v}) ,
    'notes'   :  lambda d,v: d.update({'Notes':v}) ,
    'phone'   :  lambda d,v: d.update({'PrimaryPhone': {'FreeFormNumber': v}}) ,
    'email'   :  lambda d,v: d.update({'PrimaryEmailAddr': {'Address': v}}) ,
    'QBOID'   :  lambda d,v: d ,   # That's right, do nothing.
}


blankcustomer = {}




def build_something(bag,fieldlist):
    thing = {}
    
    for k,v in bag.items():
        if k in fieldlist:
            fieldlist[k](thing,v)
        else:
            thing[k] = v
    return(thing)


def build_cust( bag ) :
    return build_something(bag,custfields)

def build_invoice(bag):
    thing = blankinvoice

    thing['Line'][0]['Amount'] = bag['amount']
    thing['CustomerRef']['value'] = int(bag['customer'])

    return(thing)



            
invoiceItem = {
    "value": 21,
    "name" : "Services",
}


InvoiceLine = {
    "Amount"     : 35.00,
    "DetailType" : "SalesItemLineDetail",
    "SalesItemLineDetail": { "ItemRef": invoiceItem  }
    }

blankinvoice = { "CustomerRef": { "value": 58},
            "Line" : [
                InvoiceLine
                ]
            }




#   "DepositToAccountRef" : { "value": "4" }


blankpayment = {
    "TotalAmt": 25.0, 
    "PaymentRefNum" : "LookMaRef",
    "ProcessPayment": True,
    "CustomerRef": {
    "value": "66"
    },
    "Line":
    [
      {
        "Amount": 5.0, 
        "LineEx": {
          "any": [ ]
        }, 
        "LinkedTxn": [
          {
            "TxnId": "150", 
            "TxnType": "Invoice"
          }
        ]
      }
    ]
}


def create_payment(bag):
    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/payment"
    querystring = {"minorversion":"14"}


    #     payment = build_payment({'customer': bag['QBOID'],'amount':35.00 })

    payment = blankpayment
    
    payload = json.dumps(payment,indent=4,sort_keys=True)

    print(payload)
    
    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "Bearer "+Token,
        'Cache-Control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    resj = json.loads(response.text);

    if("Fault" in resj):
        print(json.dumps(resj,sort_keys=True,indent=4))
        raise(Exception("Failed to add payment"))

    return resj
    





def create_invoice(bag):
    
    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/invoice"
    querystring = {"minorversion":"14"}

    print(blankinvoice)
    
    invoice = build_invoice({'customer': bag['QBOID'],'amount':35.00 })

    payload = json.dumps(invoice,indent=4,sort_keys=True)

    print(payload)
    
    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "Bearer "+Token,
        'Cache-Control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    resj = json.loads(response.text);

    if("Fault" in resj):
        print(json.dumps(resj,sort_keys=True,indent=4))
        raise(Exception("Failed to add invoice"))

    return resj
    
def create_cust(custbag):

    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/customer"
    querystring = {"minorversion":"14"}

    newcust = build_cust(custbag)

    payload = json.dumps(newcust,sort_keys=True,indent=4)

    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "Bearer "+Token,
        'Cache-Control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    resj = json.loads(response.text);

    if("Fault" in resj):
        print(json.dumps(resj,sort_keys=True,indent=4))
        raise(Exception("Failed to add user"))

    return resj['Customer']
    


def update_customer_name(id,name):

    before = get_cust(id)

    sync = int(before['Customer']['SyncToken'])

    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/customer"
    querystring = {"minorversion":"14"}

    newcust = {
        "SyncToken": sync,
        "Id": id,
        "DisplayName": name,
        "sparse": True
    }

    payload = json.dumps(newcust,sort_keys=True,indent=4)

    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "Bearer "+Token,
        'Cache-Control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

    resj = json.loads(response.text);

    if("Fault" in resj):
        print(json.dumps(resj,sort_keys=True,indent=4))
        raise(Exception("Failed to modify user"))



def get_cust(id):

    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/customer/{0}".format(id)

    querystring = {"minorversion":"14"}

    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "Bearer "+Token,
        'Cache-Control': "no-cache",
    }

    payload=""
    
    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

    resj = json.loads(response.text);

    if("Fault" in resj):
        print(json.dumps(resj,sort_keys=True,indent=4))
        raise(Exception("Failed to modify user"))

    return(resj)



    

def query(sql):

    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/query"
    
    querystring = {"minorversion":"14"}

    payload = sql

    Token = authbag['token'];

    headers = {
        'Accept': "application/json",
        'Content-Type': "application/text",
        'Authorization': "Bearer "+Token,
        'Cache-Control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    
    resj = json.loads(response.text);

    return(resj)
