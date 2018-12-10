#!/usr/bin/env python 
"""record_stripe_payments

Read our payments from Stripe, and apply them to Quickbooks.


Usage:
  record_stripe_payments [options]
  


Options:
  --debug                  Print debugging output. [default: False]
  --starting=<DATE>        Process payments on or after this date. [default: 2018-11-01]
  --ending=<DATE>          Process payments on or after this date. [default: 2018-12-30]







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
from datetime import date,datetime
from dateutil.parser import parse




def main():

    cols_we_want = {
        "QBO ID"        : "QBOID",
        "Name"          : "name",
        "Email"         : 'email',
        "Phone Number"  : 'phone',
        "Stripe ID"     : 'stripe_id',
    }

    customers =  hu.active_cust_df(cols_we_want)


    stripe.api_key = hu.get_auth_bag()['stripe_keys']['live']


    charges = stripe.Charge.list(limit=5)

    # intents = stripe.PaymentIntent.list(
    #     limit=50,
    #     created= {
    #         'gt' : int(arguments['--starting'].timestamp()),
    #         'lte': int(arguments['--ending'].timestamp())
    #     }
    #     )

    
    for charge in charges.auto_paging_iter():

        charge.transaction_date = datetime.utcfromtimestamp(charge.created)
        charge.cdate = charge.transaction_date.strftime("%Y-%m-%d %H:%M:%S")
        
        charge.amount = charge['amount']/100.0 # Convert to dollars

        # stripe customer: charge['customer']
        # Dollars: charge['amount'] / 100.0


        print("{cdate}: ${amount:,.2f}  ".format(**charge))
        
        custrow = customers.loc[customers['stripe_id'] == charge['customer']]

        if (len(custrow)) > 1:
            print("More than one customer matches customer ID {}; skipping.".format(charge['customer']))
            continue

        if (len(custrow)) == 0:
            print("Failed to find matching customer for ID {}; skipping.".format(charge['customer']))
            continue


        custrow = custrow.to_dict(orient='records')[0]
        
        payment = qu.makeStripePayment(custrow,charge)


                  

        import pdb; pdb.set_trace()

        


    # index=1
    # row=customers.iloc[[index]]
    # custID = row['QBOID']


    # stripeinfo={
    #     'amount'     : 70.00,
    #     'paymentref' : "pmt_123123123123",
    #     'transaction_date' : date.today()
    # }



    
    # payment['DepositToAccountRef'] = {'value':p_cfg['payment_account']}
    
    # qu.addInvoicesToPaymentUntilYouChoke(payment)
    
    # print(json.dumps(payment,indent=4,sort_keys=True))
    
    # # qu.record_transfer(1.95 ,124 ,158 ,date.today())
    
    # qu.record_purchase(amount=1.09,
    #                    src   =  p_cfg['payment_account'],
    #                    dest  =  p_cfg['fee_account'],
    #                    tdate =  stripeinfo['transaction_date'],
    #                    custref=int(custID) ,
    #                    description="Stripe fees for payment {paymentref}".format(**stripeinfo))


    # response = qu.record_payment(payment);

    # # print(json.dumps(response,sort_keys=True,indent=4))

    # # import pdb; pdb.set_trace()

    

    


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']

    arguments['--starting'] = parse( arguments['--starting'])
    arguments['--ending'] = parse( arguments['--ending'])

    
    if (debug): qu.debug=True

    if (debug): print(arguments)

    main()
