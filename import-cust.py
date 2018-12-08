#!/usr/bin/env python 

import requests
import json
import hackerspace_utils as hu
import qbo_utils as qu;
import pandas as pd;



#
# Export the Master Member List as csv, and put it here.
#


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


# subset[['Name','STATUS','Stripe ID','Phone Number','Email']]

debug = True



sheets['cust']      = "";
sheets['obs_qboid'] = "";


for index, row in subset.iterrows():

    cust = None

    print("# Looking for {name}. ".format(**row))

    # If they just told us which ID, then believe them.
    if ( not (row['QBOID'] == "")):
        if (debug): print("Got ID from row")
        cust = qu.query("select * from Customer where Id = '{0}'".format(int(row['QBOID'])))
        cust = cust['QueryResponse']['Customer'][0]

    # Maybe match on email?
    if( cust is None and  not ( row['email'] is None)):
        cust = qu.query("select * from Customer where PrimaryEmailAddr = '{0}'".format(row['email']))
        if ("QueryResponse" in cust) and ("Customer" in cust['QueryResponse']) and len(cust['QueryResponse']['Customer']) == 1 :
            if (debug): print("Inferred ID from email.")
            cust = cust['QueryResponse']['Customer'][0]
        else:
            cust = None  #Reset to empty.
            
    # Maybe match on Name?
    if( cust is None and  not ( row['name'] is None)):
        cust = qu.query("select * from Customer where DisplayName = '{0}'".format(row['name']))
        if ("QueryResponse" in cust) and ("Customer" in cust['QueryResponse']) and len(cust['QueryResponse']['Customer']) == 1 :
            if (debug): print("Inferred ID from name.")
            cust = cust['QueryResponse']['Customer'][0]
        else:
            cust = None


    if ( cust is None):
        # OK, we could not find them.  Time to add them.

        print("# No match found for {name}; adding. ".format(**row))

        cust = qu.create_cust(row)
    
        
    sheets.loc[index,'cust'] = json.dumps(cust)
    sheets.loc[index,'obs_qboid'] = cust['Id']

sheets['QBO ID'] = sheets['QBO ID'].fillna(0)
sheets = sheets.astype({'QBO ID':int,'obs_qboid':int})

mismatched = sheets[sheets['obs_qboid'] != sheets['QBO ID']]

# import pdb; pdb.set_trace()


for index,row in mismatched.iterrows():

    print(" Update row {ID} ({Name}) to QBO id '{obs_qboid}'".format(**row))



