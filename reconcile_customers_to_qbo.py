#!/usr/bin/env python 
"""reconcile_customers_to_qbo. 

Compare the downloaded customer list to the population of customers in Quickbooks.

Suggest modifications.


Usage:
  reconcile_customer_to_qbo [options]


Options:
  --debug                  Print debugging output. [default: False]

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
from datetime import date

from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects import Account



# Get data from the spreadsheet download

cols_we_want = {
    "QBO ID"        : "QBOID",
    "Name"          : "name",
    "Email"         : 'email',
    "Phone Number"  : 'phone',
    "Stripe ID"     : 'stripe_id',
}

all_cust = hu.all_cust_df(cols_we_want)


# Connect to  QBO


authbag = hu.get_auth_bag()


session_manager = Oauth2SessionManager(
    client_id=authbag['realm'],
    client_secret=authbag['secret'],
    access_token=authbag['token'],
    base_url=authbag['redirect'],
)


client = QuickBooks(
     sandbox=True,
     session_manager=session_manager,
     company_id=authbag['realm']
 )










# Everyone in the spreadsheet should have a record in QBO, active or not. 
#
# Everyone in QBO should have a line in the spreadsheet. 
#
# If there's a conflict, we think that the spreadsheet should win.
#







def forward():


    ccount = 0;
    pcount = 0;


    for index,row in all_cust.iterrows():

        ccount += 1

        
        if (row['QBOID'] == "" ):
            print("NO QBO for {name}".format(**row))
        else:
            if (debug) :print("{name} has QBOID '{QBOID}'".format(**row))
            

            thiscust = Customer.get(int(row['QBOID']),qb=client)
            thisj = thiscust.to_json()
            import pdb; pdb.set_trace()

        
    print("Evaluated '{0}' customers.".format(ccount))
    print("Found '{0}' problems.".format(pcount))

    if (pcount > ccount):
        print("More problems than customers!  \nYOU WIN A PRIZE!")







def main():

    forward();

    

    



if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']

#    if (debug): api_functions.debug=True
    if (debug): print(arguments)

    main()
