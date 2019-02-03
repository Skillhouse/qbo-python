#!/usr/bin/env python 
"""record_invoices. 

Record invoices.  

For each customer, infer from their memebership type the amount for
which they should be invoiced.  Record an invoice dated the first of
this month for that amount.

Optionally, specify one customer, or override date or amount. 



Usage:
  record_invoices [options]
  record_invoices --all-customers [options]


Options:
  --debug                  Print debugging output. [default: False]
  --date=<INVDATE>         The date of record for the invoice.  [default: the first]    

  --all-customers          Create invoices for all active customers [default: False]
  --custid=<ID>            Create an invoice for this particular customer [default: -1]

  --amount=<AMT>           Override amount of the invoice(s).
  --description=<DESC>     Override description on the invoice(s). 

  --inactive               Permit assigning invoices to inactive customers [default: False]


  --doit                   Actually send the invoices.  Otherwise, is a no-op. [default: False]
  --nobatch                DO NOT send in batches.   [default: False]
  --batchsize=<SIZE>       Size of batches to send   [default: 10]

"""


from docopt import docopt
import requests
import json
import hackerspace_utils as hu
import qbo_utils as qu;
import pandas as pd;
import sys
import dateparser

from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects import Account
from quickbooks.objects import Invoice
from quickbooks.objects import Item
from quickbooks.batch import batch_create
from quickbooks.objects.detailline import *


cols_we_want = {
    "QBO ID"        : "QBOID",
    "Name"          : "name",
    "Email"         : 'email',
    "Phone Number"  : 'phone',
    "TYPE"          : 'type',
    "Join Date"     : 'joindate',
}

authbag = hu.get_auth_bag()

def make_invoice():
    pass


def display_invoice(inv):

    bag = {}
    
    fmt="{name}: {amount}, on {date} "

    bag['name']   = inv.CustomerRef.name
    bag['amount'] = inv.TotalAmt
    bag['date']   = inv.TxnDate
    
    return fmt.format(**bag)


def do_batch(thebatch,qbo_client):
    if(debug):
        print("Batch create..")
    results = batch_create(thebatch,qb=qbo_client)
                    
    if (len(results.faults) > 0):
        print("Invoice submission errors...")
        print("\n".join([x.to_json() for x in results.faults]))
        sys.exit()

    return results
        



def main():
    global subset
    total_amount = 0
    
    if (arguments['--inactive']):
        subset = hu.all_cust_df(cols_we_want)
    else:
        subset = hu.active_cust_df(cols_we_want)

        
    qbo_client = qu.open_qbo_client()


    
    thedate = arguments['--date']

    itemlist = pd.DataFrame([ { 'obj':item , 'desc': item.Description , 'id': int(item.Id)}  for item in  Item.filter(qb=qbo_client) ])  

    qbolist = pd.DataFrame([ { 'obj':cust , 'id': int(cust.Id)}  for cust in qu.cust_iterable(Active=True) ])  


    if ( arguments['--custid'] != -1 ):
        if (debug):
            print("# Custid '{0}' specified. ".format(arguments['--custid']))

        subset = subset[subset['QBOID'] == arguments['--custid']]

        newlen = len(subset)
        if (newlen != 1):
            print("# More than one customer matched '{0}'?  fail.".format(arguments['--custid']))
            print(subset)
            sys.exit()



    batch = []

    count = 0

    for index, row in subset.iterrows():

        cust =qbolist[qbolist['id']==int(row['QBOID'])].iloc[0]['obj']

        if(debug): print("# Processing {name} ".format(**row))
        
        if ( arguments['--date'].date() < dateparser.parse(row['joindate']).date() ):
            # Is the date of before this person joined?
            print("# Invoice date precedes member join date; skipping.")
            continue

        myinv = qu.build_invoice(itemlist,cust,row,thedate)
        
        if(not (arguments['--description'] is None)):
            myinv.CustomerMemo = {'value': arguments['--description']}

        total_amount += myinv.TotalAmt
            
        myinv.TxnDate = arguments['--date'].date().isoformat()
        
        print(display_invoice(myinv))
        count += 1

        if (arguments['--doit']):
            if ( arguments['--nobatch'] ) :
                myinv = myinv.save(qb=qbo_client)
            else:
                batch.append(myinv)
                if (len(batch) >= arguments['--batchsize']):
                    results = do_batch(batch,qbo_client)
                    batch = []

        else:
            print ("# Not saving")

    if ( len(batch) > 0  and arguments['--doit'] ):
        results = do_batch(batch,qbo_client)

    print(" Found {0} invoices to submit. ".format(count))

            

if __name__ == '__main__':

    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug     = arguments['--debug']


    arguments['--batchsize'] =  int(arguments['--batchsize'])
    arguments['--custid'] =     int(arguments['--custid'])

    
    #    if (debug): api_functions.debug=True

    if ( arguments['--date'] == "the first" ) :
        arguments['--date'] = dateparser.parse("{0} days ago".format(dateparser.parse("today").day -1 ))
    else:
        arguments['--date'] = dateparser.parse(arguments['--date'])


    if (arguments['--doit'] ) :
        qu.doit =True;
    else: 
        print("\n Not saving invoices.  Specify '--doit' or get a no-op\n")

        
    if (debug):
        hu.debug = True;
        qu.debug=True
        print(arguments)




    main()
