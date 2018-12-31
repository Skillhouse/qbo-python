#!/usr/bin/env python 
"""listaccounts -- 

List accounts from QBO.



Usage:
  listaccounts.py  [options]

Options:
  --debug                  Print debugging output. [default: False]

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
from quickbooks.objects import Account
from quickbooks.batch import batch_delete



import qbo_utils as qu

#
# Still thinking about how to parameterize this.  While it's clumsy,
# it'll stay broken out here.
#

qbo_client = None

def account_iterable(whereclause="",**kwargs):
    reps = 0
    yielded = 0
    
    while (True):
        
        accounts = Account.where(whereclause,
            qb=qbo_client,
            max_results=100,
            start_position=yielded+1,
            **kwargs
        )
        reps += 1

        if len(accounts) == 0:
            return

        for item in accounts:
            yielded += 1
            yield(item)



def account2row(inv):
    bag = {
        'AccountType'    : inv.AccountType,
        'AccountSubType' : inv.AccountSubType,
        'Name'           : inv.Name,
        'Id'             : inv.Id,
    }
    return(bag)
    

def main():
    global qbo_client
    qbo_client = qu.open_qbo_client()


    whereclause = "" 
        
    
    ilist = pd.DataFrame( [ account2row(inv) for inv in account_iterable(whereclause=whereclause)])
    if (len(ilist) == 0 ) :
        print("No matches for your query: \n---\n{0}\n---\n".format(whereclause))
        sys.exit()

    ilist['Id'] = ilist['Id'].astype(int)
    print(ilist)

    bag = {}
    bag['icount'] = len(ilist)
    

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']


    if (debug):
        qu.debug=True
        hu.debug=True
        print(arguments)

    main()
