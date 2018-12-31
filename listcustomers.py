#!/usr/bin/env python 
"""listcustomers -- 

List customers from QBO.



Usage:
  listcustomers.py  [options]

Options:
  --debug                  Print debugging output. [default: False]

  --custid <id[,id...]>    List for specified QBO IDs. 


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
import dateparser

from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects import Account
from quickbooks.objects import EmailAddress
from quickbooks.objects import Customer
from quickbooks.batch import batch_delete



import qbo_utils as qu

#
# Still thinking about how to parameterize this.  While it's clumsy,
# it'll stay broken out here.
#

qbo_client = None

def customer_iterable(whereclause="",**kwargs):
    reps = 0
    yielded = 0
    
    while (True):
        
        customers = Customer.where(whereclause,
            qb=qbo_client,
            max_results=100,
            start_position=yielded+1,
            **kwargs
        )
        reps += 1

        if len(customers) == 0:
            return

        for item in customers:
            yielded += 1
            yield(item)



def customer2row(inv):
    bag = {
        'DisplayName'   : inv.DisplayName,
        'email'         : "" if inv.PrimaryEmailAddr is None else inv.PrimaryEmailAddr.Address,
        'Id'            : inv.Id,
    }
    return(bag)
    

def main():
    global qbo_client
    qbo_client = qu.open_qbo_client()


    sqlbits = [];
       
    if not arguments['--custid'] is None:
        custs = "CustomerRef in (" + ",".join("'{0}'".format(str(i)) for i in arguments['--custid']) + ")"
        sqlbits.append(custs)

    whereclause = ""
        
    
    ilist = pd.DataFrame( [ customer2row(inv) for inv in customer_iterable(whereclause=whereclause)])
    if (len(ilist) == 0 ) :
        print("No matches for your query: \n---\n{0}\n---\n".format(whereclause))
        sys.exit()

    ilist['Id'] = ilist['Id'].astype(int)

    #import pdb; pdb.set_trace()

    for k,row in ilist.iterrows():
        print("{Id},{DisplayName},{email}".format(**row))

   
    

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']

    if (arguments['--custid']):
        arguments['--custid'] = [ int(x) for x in arguments['--custid'].split(",")]
 

    if (debug):
        qu.debug=True
        hu.debug=True
        print(arguments)

    main()
