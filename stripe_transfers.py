#!/usr/bin/env python 
"""record_stripe_transfers

Read our transfers from Stripe, and apply them to Quickbooks.


Usage:
  record_stripe_transfers [options]
  


Options:
  --debug                  Print debugging output. [default: False]
  --starting=<DATE>        Process transfers on or after this date. [default: the first]
  --ending=<DATE>          Process transfers before this date. [default: today]


  --doit                   Actually commit the transfer records.  Otherwise, is a no-op.  [default: False]
  --nobatch                DO NOT send in batches.   [default: False]
  --batchsize=<SIZE>       Size of batches to send   [default: 8]





"""
from docopt import docopt
import requests
import json
import hackerspace_utils as hu
import qbo_utils as qu;
import pandas as pd;
import sys
import time
import stripe;
from datetime import date,datetime,timedelta
# from dateutil.parser import parse
import dateparser

from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects import Account
from quickbooks.objects import Invoice
from quickbooks.objects import Payment
from quickbooks.objects import Transfer
from quickbooks.objects import Item
from quickbooks.batch import batch_create
from quickbooks.objects.detailline import *




authbag = hu.get_auth_bag()

session_manager = Oauth2SessionManager(
    client_id=authbag['realm'],
    client_secret=authbag['secret'],
    access_token=authbag['token'],
    base_url=authbag['redirect'],
)

client = QuickBooks(
#     sandbox=True,
     session_manager=session_manager,
     company_id=authbag['realm']
 )


def xfr_iterable(whereclause):

    bitesize = 100
    reps=0
    yielded = 0
    
    while (True):

        transfers = Transfer.where(whereclause,
                                 qb=client,
                                 max_results=bitesize,
                                 start_position=yielded+1)
        reps += 1

        if len(transfers) == 0:
            return

        for item in transfers:
            yielded += 1
            yield(item)


def charge_summary(thecharge):
    return("{cdate}:{id}:${amount:,.2f} -- {receipt_email}".format(**thecharge))

def trans_summary(thetrans):
    return("# {cdate}:{id}:${amount:,.2f} -- ".format(**thetrans))

#        print("{cdate}: ${amount:,.2f}  ".format(**charge))

def main():

    stripe.api_key = hu.get_auth_bag()['stripe_keys']['live']

    src_acct_id  = hu.get_paymentconfig()['stripe']['payment_account']
    dest_acct_id = hu.get_paymentconfig()['bank']['payment_account']

    transfers = stripe.Transfer.list(limit=20,
                                 date= {
                                     'gte' : int(arguments['--starting'].timestamp()),
                                     'lte': int(arguments['--ending'].timestamp())
                                 },
                                 )

    #
    # Get already-recorded transactions from quickbooks; spread the
    # net a little wider than we expect to be necessary.
    #

    
    whereclause = " TxnDate >= '{starts}' and TxnDate <= '{ends}' ".format(**{
        'starts' :  (arguments['--starting'] - timedelta(days=1)).date().isoformat(),
        'ends'   :  (arguments['--ending']   + timedelta(days=1)).date().isoformat(),
    })
            
    existing_transfers = { xfr.PrivateNote: xfr  for xfr in xfr_iterable( whereclause )}
    
    for trans in transfers.auto_paging_iter():
        
        trans.transaction_date = datetime.utcfromtimestamp(trans.date)
        trans.cdate = trans.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
        trans.amount = trans['amount']/100.0

        print("\n# Processing "+trans_summary(trans))


        if trans.id in existing_transfers:
            print("# Already recorded this transfer.  Skipping.")
            continue
        
        qu.record_transfer(
            amount = trans.amount,
            src=src_acct_id,
            dest=dest_acct_id,
            tdate=trans.transaction_date,
            docid=trans.id,
        )

        time.sleep(1)
   

    

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']
    doit = arguments['--doit']

    if ( arguments['--starting'] == "the first" ) :
        arguments['--starting'] = dateparser.parse("{0} days ago".format(dateparser.parse("today").day -1 ))
    else:
        arguments['--starting'] = dateparser.parse(arguments['--starting'])

    arguments['--ending'] = dateparser.parse( arguments['--ending'])


    if (doit):  qu.doit =True;

    if (debug):
        qu.debug=True;
        hu.debug = True
        print(arguments)

    main()
