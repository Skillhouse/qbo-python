#!/usr/bin/env python 

import requests
import json
import hackerspace_utils as hu
import qbo_utils as qu;
import pandas as pd;
import sys
import time
from datetime import date


# Export the Master Member List as csv, and put it here.


csvin="../memberlist.csv"

sheets = pd.read_csv(csvin,header=1)

sheets = sheets.loc[sheets['STATUS'] == 'ACTIVE']

cols_we_want = {
    "QBO ID"        : "QBOID",
    "Name"          : "name",
    "Email"         : 'email',
    "Phone Number"  : 'phone',
    }

subset = sheets.filter(items=cols_we_want.keys())
subset = subset.rename(axis="columns",mapper=cols_we_want)
subset = subset.fillna("")

debug = True


p_cfg = hu.get_paymentconfig()['stripe']



index=1
row=subset.iloc[[index]]

custID = row['QBOID']


stripeinfo={
    'amount'     : 70.00,
    'paymentref' : "pmt_123123123123",
    'transaction_date' = date.today()
    }



payment = qu.makeStripePayment(row,stripeinfo)

payment['DepositToAccountRef'] = {'value':p_cfg['payment_account']}

qu.addInvoicesToPaymentUntilYouChoke(payment)

print(json.dumps(payment,indent=4,sort_keys=True))

# qu.record_transfer(1.95 ,124 ,158 ,date.today())

qu.record_purchase(amount=1.09,
                   src   =  p_cfg['payment_account'],
                   dest  =  p_cfg['fee_account'],
                   tdate =  stripeinfo['transaction_date']
                   custref=int(custID) ,
                   description="Stripe fees for payment {paymentref}".format(**stripeinfo))


# response = qu.record_payment(payment);

# print(json.dumps(response,sort_keys=True,indent=4))

# import pdb; pdb.set_trace()
    


