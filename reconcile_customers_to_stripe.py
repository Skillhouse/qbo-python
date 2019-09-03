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
    "QBO ID"             : "QBOID",
    "Name"               : "name",
    "TYPE"               : "type",
    "STATUS"             : "status",
    "Email"              : 'email',
    "Phone Number"       : 'phone',
    "Stripe ID"          : 'stripe_id',
    "Automatic payments" : 'auto_style',
}

all_cust = hu.all_cust_df(cols_we_want)

all_cust['email'] = all_cust['email'].str.lower()





stripe.api_key = hu.get_auth_bag()['stripe_keys']['live']

plans = {
    'REGULAR' : 'reg2014',
    'STUDENT' : 'studmem',
    }


def desired_subscription(cust):
    # Interpret our spreadsheet, picking a plan
    # based on our data.

    if (cust['status'] != 'ACTIVE'):
        return None

    if (cust['email'] == 'eddie@reidehome.com'):
        # If we get more than a few of these, they should really
        # be a column in the database.
        return None

    if (cust['auto_style'] == 'No'):
        # Here's a column in the database.
        return None


    
    return plans[cust['type']]
    


def compare_notes(ourdata,stripedata):

    ourdict = ourdata.to_dict('records')[0]

    if(stripedata['email'] == ourdict['email']):
        if (debug): print("#  Emails match ")
    else:
        ourdict['stripemail'] = stripedata['email']
        print("#  Emails differ; ours:({email}) stripe:({stripemail}) ".format(**ourdict))


        
    ourdict['oursub']    = desired_subscription(ourdict)
    ourdict['stripesubs'] = [sub['plan']['id'] for sub in stripedata['subscriptions']['data'] ]

    ourdict['sss'] = ",".join(ourdict['stripesubs'])
    
    if(debug):
        print ("#  type: {type} ({oursub}); stripe has: {sss}".format(**ourdict) )

    if (( (ourdict['oursub'] is None  ) and ( len(ourdict['stripesubs']) == 0))  or
        ( ourdict['oursub'] in ourdict['stripesubs']) ):
        # All good
        if (debug): print("#  That's a match.")
    else:
        print("#  {email} should have sub '{oursub}'; has '{sss}'. ".format(**ourdict))
        
    
      
    

def main():

    customers = stripe.Customer.list(limit=20)

    ccount = 0;
    pcount = 0;

    for customer in customers.auto_paging_iter():

        if (debug): print("# customer '{id}' ({email})".format(**customer))

        customer['email'] = customer['email'].lower()

        found = {}
    
    
        if not (customer['id'] in all_cust['stripe_id'].values):
            pcount +=1 ;
            print("ERR: No sheets reference for ID '{id}' ".format(**customer))
        else:
                if (debug): print("#  Found stripe ID. ".format(**customer))
                found['id'] = all_cust[all_cust['stripe_id']==customer['id']].index.values.tolist()
                if (len(found['id']) > 1):
                    pcount +=1 
                    print("ERR: multiple matches for ID {1}. ({0}) ".format(",".join(str(x) for x in found['id']),customer['id']))
                else:
                    # OK, now we've got a single match.  
                    compare_notes( all_cust[all_cust['stripe_id']==customer['id']],customer)
                


                    
        
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
