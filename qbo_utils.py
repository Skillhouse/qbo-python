

import requests
import json
import hackerspace_utils as hu
import sys
import copy

import time
from datetime import date

from operator import itemgetter

from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects import Account


debug = False


authbag = hu.get_auth_bag()
Token = authbag['token'];


custfields = {
    'name'      :  lambda d,v: d.update({'DisplayName':v}) ,
    'phone'     :  lambda d,v: d.update({'PrimaryPhone': {'FreeFormNumber': v}}) ,
    'email'     :  lambda d,v: d.update({'PrimaryEmailAddr': {'Address': v}}) ,
    'QBOID'     :  lambda d,v: d ,   # No place in object
    'stripe_id' :  lambda d,v: d ,   # No place in object
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
    "TotalAmt": 0.0, 
    "UnappliedAmt": 0.0,
    "PaymentRefNum" : "NeedToSetThis",
    "ProcessPayment": True,
    "CustomerRef": {
    "value": "-1"
    },
    "Line":
    [
      {
        "Amount": 0.0, 
        "LineEx": {
          "any": [ ]
        }, 
        "LinkedTxn": [
        ]
      }
    ]
}

blankpayment = {
    "TotalAmt": 0.0, 
    "UnappliedAmt": 0.0,
    "PaymentRefNum" : "NeedToSetThis",
    "ProcessPayment": True,
    "CustomerRef": {
    "value": "-1"
    },
    "Line":
    [
    ]
}




blanktransfer ={
    "Amount": "1.95",
    "ToAccountRef": {
        "value": "158"
    }, 
    "FromAccountRef": {
        "value": "124"
    }
}



blankpurchase = {
  "PaymentType": "Cash", 
  "AccountRef": {
    "name": "Undeposited Funds", 
    "value": 124
  }, 
  "Line": [
    {
      "DetailType": "AccountBasedExpenseLineDetail", 
      "Amount": 2.34, 
      "AccountBasedExpenseLineDetail": {
        "AccountRef": {
          "name": "Stripe Fees", 
          "value": 166
        }
      }
    }
  ]
}






def makeStripePayment(customer,stripeinfo):
    import pdb; pdb.set_trace()

    payment = copy.deepcopy(blankpayment);

    payment['CustomerRef']['value'] = int(customer['QBOID'])

    payment['TotalAmt'] = payment['UnappliedAmt'] = stripeinfo['amount']

    payment['PaymentRefNum'] = stripeinfo['id']
    
    payment['TxnDate'] = stripeinfo['transaction_date']
    
    return payment
    



def addInvoicesToPaymentUntilYouChoke(payment):

    id=payment['CustomerRef']['value'];
    
    dcount = count_of_open_invoices_for_customer(id)

    if(dcount <1):
        # No open invoices.  We choke at the starting gate.
        return(payment)

    # Now we apply open invoices, until we run out of invoices or run
    # out of payment balance.

    
    alist = query_open_invoices_for_customer(id)
    
    for item in sorted(alist, key=itemgetter('DueDate') )  :
#        print( json.dumps(item,indent=4,sort_keys=True))


        amtToThisInvoice = min(payment['UnappliedAmt'],item['Balance'])

        txline = {"Amount": amtToThisInvoice,
                  "LinkedTxn": [ {'TxnType': "Invoice",
                                "TxnId": item['Id']} ]
                  }

        payment['Line'].append(txline)
        
        print ("Item: {0} Remaining: {1}  Amt: {2}".format(item['Balance'],payment['UnappliedAmt'],amtToThisInvoice));

        payment['UnappliedAmt'] -= amtToThisInvoice
        
        if (  payment['UnappliedAmt'] <= 0 ) :
            payment['UnappliedAmt'] = 0
            break  # We're out of payment.

    return(payment)



def record_payment(payment):
    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/payment"
    querystring = {"minorversion":"14"}

    payload = json.dumps(payment,indent=4,sort_keys=True)

    
    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "Bearer "+Token,
        'Cache-Control': "no-cache",
    }

    resj={}

    if (debug):
        print(payload)
        
    else: 
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        resj = json.loads(response.text);

    if("Fault" in resj):
        print(json.dumps(resj,sort_keys=True,indent=4))
        raise(Exception("Failed to add payment"))

    return resj
    



def record_transfer(amount,src,dest,tdate):
    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/transfer"
    querystring = {"minorversion":"14"}


    transfer = copy.deepcopy(blanktransfer)

    transfer['Amount'] = amount
    transfer['ToAccountRef']['value'] = int(dest)
    transfer['FromAccountRef']['value'] = int(src)
    transfer['TxnDate'] = tdate.isoformat()
    
    payload = json.dumps(transfer,indent=4,sort_keys=True)

    print(payload)

    import pdb; pdb.set_trace()
    
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
        raise(Exception("Failed to record transfer"))

    return resj


def record_purchase(amount,src,dest,tdate,custref,description):

    # Purchases are _us_ buying things, we're spending money. 

    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/purchase"
    querystring = {"minorversion":"14"}


    item = copy.deepcopy(blankpurchase)

    lineitem = { "DetailType": "AccountBasedExpenseLineDetail",
                 "Amount": amount,
                 "Description" : description,
                 "AccountBasedExpenseLineDetail": {
                     "AccountRef"  : { "value": dest },
                     "CustomerRef" : { "value": custref  },
                 } }

    
    item['Line'] = [ lineitem ]
    
    item['AccountRef'] = { 'value': src}
    
    item['TxnDate'] = tdate.isoformat()


    payload = json.dumps(item,indent=4,sort_keys=True)


   
    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "Bearer "+Token,
        'Cache-Control': "no-cache",
    }

    resj={}

    if (debug): 
        print(payload)
    else:    
        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
        resj = json.loads(response.text);

    if("Fault" in resj):
        print(json.dumps(resj,sort_keys=True,indent=4))
        raise(Exception("Failed to record purchase"))

    return resj




def record_invoice(custrow):
    
    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/invoice"
    querystring = {"minorversion":"14"}

    print(blankinvoice)
    
    invoice = build_invoice({'customer': custrow['QBOID'],'amount':35.00 })

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
    
def create_cust(custrow):

    url = "https://sandbox-quickbooks.api.intuit.com/v3/company/123146047051614/customer"
    querystring = {"minorversion":"14"}

    newcust = build_cust(custrow)

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



def count_of_open_invoices_for_customer(id):
    sql="select count(*) from Invoice where CustomerRef = '{0}' AND Balance > '0.0'  startposition 1 maxresults 5".format(int(id))

    resj=query(sql)

    if("Fault" in resj):
        print(json.dumps(resj,sort_keys=True,indent=4))
        raise(Exception("invoice count query failed."))

    return(resj['QueryResponse']['totalCount'])

    

def query_open_invoices_for_customer(id):
    
    sql="select * from Invoice where CustomerRef = '{0}' AND Balance > '0.0'  startposition 1 maxresults 5".format(int(id))

    resj=query(sql)
    
    if("Fault" in resj):
        print(json.dumps(resj,sort_keys=True,indent=4))
        raise(Exception("invoice query failed."))
    
    return(resj['QueryResponse']['Invoice'])
    
