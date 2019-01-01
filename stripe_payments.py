#!/usr/bin/env python 
"""record_stripe_payments

Read our payments from Stripe, and apply them to Quickbooks.


Usage:
  record_stripe_payments [options]
  


Options:
  --debug                  Print debugging output. [default: False]
  --starting=<DATE>        Process payments on or after this date. [default: 2018-11-01]
  --ending=<DATE>          Process payments on or after this date. [default: 2018-12-30]


  --doit                   Actually commit the payment records.  Otherwise, is a no-op.  [default: False]
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
import datetime
from datetime import date,datetime,timedelta
from dateutil.parser import parse
import dateparser

from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects import Account
from quickbooks.objects import Invoice
from quickbooks.objects import Payment
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


def pmt_iterable(whereclause):

    bitesize = 100
    reps=0
    yielded = 0
    
    while (True):

        payments = Payment.where(whereclause,
                                 qb=client,
                                 max_results=bitesize,
                                 start_position=yielded+1)
        reps += 1

        if len(payments) == 0:
            return

        for item in payments:
            yielded += 1
            yield(item)
    














def charge_summary(thecharge):
    return("{cdate}:{id}:${amount:,.2f} -- {receipt_email}".format(**thecharge))



#        print("{cdate}: ${amount:,.2f}  ".format(**charge))

def main():

    cols_we_want = {
        "QBO ID"        : "QBOID",
        "Name"          : "name",
        "Email"         : 'email',
        "Phone Number"  : 'phone',
        "Stripe ID"     : 'stripe_id',
    }

    customers =  hu.all_cust_df(cols_we_want)


    stripe.api_key = hu.get_auth_bag()['stripe_keys']['live']

    p_cfg = hu.get_paymentconfig()['stripe']

    charges = stripe.Charge.list(limit=20,
                                 created= {
                                     'gt' : int(arguments['--starting'].timestamp()),
                                     'lte': int(arguments['--ending'].timestamp())
                                 },
                                 expand=['data.balance_transaction']    )


    #
    # Get already-recorded transactions from quickbooks; spread the
    # net a little wider than we expect to be necessary.
    #

    
    whereclause = " TxnDate >= '{starts}' and TxnDate < '{ends}' ".format(**{
        'starts' :  (arguments['--starting'] - timedelta(days=1)).date().isoformat(),
        'ends'   :  (arguments['--ending']   + timedelta(days=1)).date().isoformat(),
    })
        
    existing_payments = { pmt.PaymentRefNum: pmt  for pmt in pmt_iterable( whereclause )}
    
    
    for charge in charges.auto_paging_iter():


        charge.transaction_date = datetime.utcfromtimestamp(charge.created)
        charge.cdate = charge.transaction_date.strftime("%Y-%m-%d %H:%M:%S")

        charge.amount = charge['amount']/100.0 # Convert to dollars

        if ( charge.status == "failed" ) :
            print("# Skipping failed charge: ")
            print("# "+charge_summary(charge))
            continue

        print("\n#   Processing "+charge_summary(charge))


       


        # stripe customer: charge['customer']
        # Dollars: charge['amount'] / 100.0

     
        custrow = customers.loc[customers['stripe_id'] == charge['customer']]

        if (len(custrow)) > 1:
            print("More than one customer matches customer ID {}; skipping.".format(charge['customer']))
            continue

        if (len(custrow)) == 0:
            print("Failed to find matching customer for ID {}; skipping.".format(charge['customer']))
            continue


        custrow = custrow.to_dict(orient='records')[0]
        
        payment = qu.makeStripePayment(custrow,charge)

        borkenref=payment['PaymentRefNum']
              
        if borkenref in existing_payments:
            print("# Already recorded this payment.  Skipping.")
            continue
        

        qu.addInvoicesToPaymentUntilYouChoke(payment)
    
        payment['DepositToAccountRef'] = {'value':p_cfg['payment_account']}

        response = qu.record_payment(payment);

        if ('Fault' in response):
            print("Payment submission error: dying")
            print(response)
            sys.exit()
            

        
            
        qu.record_purchase(amount=charge['balance_transaction']['fee']/100.0,  # Convert to dollars
                           src   =  p_cfg['payment_account'],
                           dest  =  p_cfg['fee_account'],
                           tdate =  charge['transaction_date'],
                           custref=int(custrow['QBOID']) ,
                           description="Stripe fees for payment {0}".format(borkenref),
                           docnum = borkenref                          
        )
        


        time.sleep(1)
   

    

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']
    doit = arguments['--doit']

    if ( arguments['--starting'] == "the first" ) :
        arguments['--starting'] = hu.dayify(dateparser.parse("{0} days ago".format(dateparser.parse("today").day -1 )))
    else:
        arguments['--starting'] = hu.dayify(dateparser.parse(arguments['--starting']))

    arguments['--ending'] = hu.dayify(dateparser.parse( arguments['--ending']))


    if (doit):  qu.doit =True;

    if (debug):
        qu.debug=True;
        hu.debug = True
        print(arguments)

    main()
