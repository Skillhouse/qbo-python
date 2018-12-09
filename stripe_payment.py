#!/usr/bin/env python 

import requests
import json
import hackerspace_utils as hu
import qbo_utils as qu;
import pandas as pd;
import sys



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



index=1
row=subset.iloc[[index]]

custID = row['QBOID']


stripebag={
    'amount'     : 70.00,
    'paymentref' : "pmt_123123123123", 
    }


paymentconfig = hu.get_paymentconfig()['stripe']

import pdb; pdb.set_trace()

payment = qu.makeStripePayment(row,stripebag)

payment['DepositToAccountRef'] = {'value':paymentconfig['payment_account']}

qu.addInvoicesToPaymentUntilYouChoke(payment)

print(json.dumps(payment,indent=4,sort_keys=True))

# response = qu.record_payment(payment);

# print(json.dumps(response,sort_keys=True,indent=4))

# import pdb; pdb.set_trace()
    


