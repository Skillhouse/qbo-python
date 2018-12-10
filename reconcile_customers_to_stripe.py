#!/usr/bin/env python 
"""reconcile_customers_to_stripe. 

Compare the downloaded customer list to the population of customers in Stripe. 

Suggest modifications.



Usage:
  reconcile_customer_to_stripe [options]



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


# Export the Master Member List as csv, and put it here.


cols_we_want = {
    "QBO ID"        : "QBOID",
    "Name"          : "name",
    "Email"         : 'email',
    "Phone Number"  : 'phone',
    "Stripe ID"     : 'stripe_id',
}

all_cust = hu.all_cust_df(cols_we_want)


stripe.api_key = hu.get_auth_bag()['stripe_keys']['live']



def main():

    customers = stripe.Customer.list(limit=20)

    ccount = 0;
    pcount = 0;

    for customer in customers.auto_paging_iter():

        if (debug): print("# customer '{id}' ({email})".format(**customer))

        customer['email'] = customer['email'].lower()
        all_cust['email'] = all_cust['email'].str.lower()

        found = {}
    
    
        if not (customer['id'] in all_cust['stripe_id'].values):
            pcount +=1 ;
            print("ERR: No sheets reference for ID '{id}' ".format(**customer))
        else:
                if (debug): print("  Found stripe ID. ".format(**customer))
                found['id'] = all_cust[all_cust['stripe_id']==customer['id']].index.values.tolist()
                if (len(found['id']) > 1):
                    pcount +=1 
                    print("ERR: multiple matches for ID {1}. ({0}) ".format(",".join(str(x) for x in found['id']),customer['id']))

        
        if not (customer['email'] in all_cust['email'].values):
            print("ERR: No sheets reference for email '{email}' ".format(**customer))
            pcount +=1 ;
        else:
            if (debug): print("  Found email. ".format(**customer))
            found['email'] = all_cust[all_cust['email']==customer['email']].index.values.tolist()
            if (len(found['email']) > 1):
                pcount +=1 ;
                print("ERR: multiple matches for email {1}. ({0}) ".format(",".join(str(x) for x in found['email']), customer['email']))

        ccount += 1;

        if ( 'email' not in found ) or ( 'id' not in found ):
            print("   Desired:  {email} matched with {id}".format(**customer))

            continue

        if not(found['email'] == found['id']):
            pcount += 1
            print("ERR: email and ID hits do not match.  ".format(",".join(str(x) for x in found['email'])))
            print(found)
            print("   Desired:  {email} matched with {id}".format(**customer))

    
        #import pdb; pdb.set_trace()



    print("Evaluated '{0}' customers.".format(ccount))
    print("Found '{0}' problems.".format(pcount))

    if (pcount > ccount):
        print("More problems than customers!  \nYOU WIN A PRIZE!")
    



if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']

#    if (debug): api_functions.debug=True
    if (debug): print(arguments)

    main()
