#!/usr/bin/env python 
"""reconcile_customers_to_qbo. 

Compare the downloaded customer list to the population of customers in Quickbooks.

Suggest modifications.


Usage:
  reconcile_customer_to_qbo [options]

Options:
  --debug                  Print debugging output. [default: False]


  --doit                   Actually modify QBO data.  Otherwise, is a no-op.  [default: False]


  --qboid <id[,id...]>     Reconcile specified comma-delimited IDs. 


"""


from docopt import docopt
import requests
import json
import hackerspace_utils as hu
import pandas as pd;
import sys
import time
import stripe;
from datetime import date

from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects import Account
from quickbooks.objects import EmailAddress
from quickbooks.objects import Address


import qbo_utils as qu



# Get data from the spreadsheet download

cols_we_want = {
    "QBO ID"        : "QBOID",
    "Name"          : "name",
    "Email"         : 'email',
    "Phone Number"  : 'phone',
    "Stripe ID"     : 'stripe_id',
}

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

    bag['obj'] = cust

    return(bag)
        





def forward():

    all_cust = hu.all_cust_df(cols_we_want)

    if (arguments['--qboid']):
        all_cust = all_cust[all_cust['QBOID'].isin(arguments['--qboid'])]


    # Connect to  QBO, and get the current list from them.
    
    qbo_client = qu.open_qbo_client()
    
    qbolist = pd.DataFrame([ cust2bag(cust) for cust in qu.cust_iterable() ])  
    qbolist['id'] = qbolist['id'].astype(int)

    if (arguments['--qboid']):
        qbolist = qbolist[qbolist['id'].isin(arguments['--qboid'])]

    
    
    ccount = 0;
    pcount = 0;

#    all_cust['QBOID']="";

    for index,row in all_cust.iterrows():

        ccount += 1
        changes = False

        
        if (row['QBOID'] == 0 ):
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
                pcount += 1
                if(arguments['--doit']):
                    print("No prospective match.  Adding. ")
                    thisj = qu.build_cust(row)
                    new = Customer.from_json(thisj)
                    newer = new.save(qb=qbo_client)
                    print("# New QBO: {0}".format(newer.Id) )
                else:
                    print("#  Not adding, because you said not to (no --doit)")
                    
                    
        else:
            if (debug) :print("{name} has QBOID '{QBOID}'".format(**row))

            
            
            thiscust = qbolist[qbolist['id']==int(row['QBOID'])].iloc[0]['obj']
            thisjson = thiscust.to_json()


            if (not thiscust.DisplayName == row['name']):
                row['qbodn'] = thiscust.DisplayName
                print( "#  QBO#{QBOID} has DisplayName '{qbodn}' instead of '{name}'. ".format(**row))
                thiscust.DisplayName = row['name']
                pcount += 1
                changes = True
            else:
                if (debug): print("  Names match")


            if (thiscust.PrimaryEmailAddr and ( thiscust.PrimaryEmailAddr.Address == row['email'] )):
                if (debug): print("  Emails are present and match")
                # Equal; all good
            elif ( thiscust.PrimaryEmailAddr is None and row['email'] == "" ) :
                if (debug): print("  Emails are absent and match")
                # Quasi-equal.  All good.
            else :
                row['qboemail'] = thiscust.PrimaryEmailAddr.Address if thiscust.PrimaryEmailAddr else "not present"
                print( "#  QBO #{QBOID} email is '{qboemail}' instead of '{email}'. ".format(**row))


                thiscust.PrimaryEmailAddr = EmailAddress()
                thiscust.PrimaryEmailAddr.Address = row['email']
                pcount += 1
                changes=True

            if(changes):
                if(arguments['--doit']):
                    print(" # Updating... ")
                    thiscust.save(qb=qbo_client)
                else:
                    print("#  Not fixing, because you said not to (no --doit)")


    print("Evaluated '{0}' customers.".format(ccount))
    print("Found '{0}' problems.".format(pcount))

    if (pcount > ccount):
        print("More problems than customers!  \nYOU WIN A PRIZE!")







def main():
    forward();

    # I was thinking we might backpropagate, but so far I think not.
    # I guess I'm unbalanced.
    

    
  


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']

    if (arguments['--qboid']):
        arguments['--qboid'] = [ int(x) for x in arguments['--qboid'].split(",")]
 
    
    if (debug):
        qu.debug=True
        hu.debug=True

    if (debug): print(arguments)

    main()
