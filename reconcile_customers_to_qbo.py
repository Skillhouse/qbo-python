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




def cust_iterable():

    bitesize = 5
    reps=0
    yielded = 0
    
    while (True):

        customers = Customer.filter(qb=client,
                                    max_results=100,
                                    start_position=yielded+1)
        reps += 1

        if len(customers) == 0:
            return

        for item in customers:
#            if (debug): print("Reps: {0}.  Yielded: {1} bitecount: {2}".format(reps,yielded,len(customers)))

            yielded += 1
            yield(item)
    











# Everyone in the spreadsheet should have a record in QBO, active or not. 
#
# Everyone in QBO should have a line in the spreadsheet. 
#
# If there's a conflict, we think that the spreadsheet should win.
#


dispformat = "'{name}' : '{email}' : '{phone}' "



def display_custrow(row):

    return dispformat.format(**row)


def cust2bag(cust):

    bag = {}

    bag['id'] = cust.Id
    bag['name']  = cust.DisplayName

    try:
        bag['email'] = cust.PrimaryEmailAddr.Address
    except AttributeError:
        bag['email'] = ""

    try:
        bag['phone'] = cust.PrimaryPhone.FreeFormNumber
    except AttributeError:
        bag['phone'] = ""

    return(bag)
        

def forward():


    
    
    qbolist = pd.DataFrame([ cust2bag(cust) for cust in cust_iterable() ])  
    
    ccount = 0;
    pcount = 0;

#    all_cust['QBOID']="";

    for index,row in all_cust.iterrows():

        ccount += 1

        
        if (row['QBOID'] == "" ):
            print("Sheet has no QBO ID for {name}".format(**row))

            found_candidate = False
            
            print(display_custrow(row))

            maybes = qbolist[(qbolist['email'] == row['email']) | (qbolist['name']==row['name'])]

            if(len(maybes) > 0):
                found_candidate = True
                print("Candidate matches: ")
                for index,cust in maybes.iterrows():
                    print(display_custrow(cust)+" (QBO: {0})".format(cust['id']) )



            if(found_candidate):
                print("Candidates exist; not adding.")
            else:
                print("No prospective match; adding. ")
                
                thisj = qu.build_cust(row)
                new = Customer.from_json(thisj)
                newer = new.save(qb=client)
                print(display_cust(newer)+" (QBO: {0})".format(newer.Id) )

        else:
            if (debug) :print("{name} has QBOID '{QBOID}'".format(**row))

#            thiscust = Customer.get(int(row['QBOID']),qb=client)
#            thisj = thiscust.to_json()

#            import pdb; pdb.set_trace()

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
