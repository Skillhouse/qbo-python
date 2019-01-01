#!/usr/bin/env python 
"""listitems -- 

List items from QBO.



Usage:
  listitems.py  [options]

Options:
  --debug                  Print debugging output. [default: False]

  --doit                   Actually do one of the optional things.  Otherwise, is a no-op. [default: False]


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
from quickbooks.objects import Item
from quickbooks.batch import batch_delete



import qbo_utils as qu

#
# Still thinking about how to parameterize this.  While it's clumsy,
# it'll stay broken out here.
#

qbo_client = None

def item_iterable(whereclause="",**kwargs):
    reps = 0
    yielded = 0
    
    while (True):
        
        items = Item.where(whereclause,
            qb=qbo_client,
            max_results=100,
            start_position=yielded+1,
            **kwargs
        )
        reps += 1

        if len(items) == 0:
            return

        for item in items:
#            import pdb; pdb.set_trace()
            yielded += 1
            yield(item)



def item2row(inv):
    bag = {
        'Id'             : inv.Id,
        'name'           : inv.FullyQualifiedName,
        'type'           : inv.Type,
        'UnitPrice'      : inv.UnitPrice,
    }

    if ( inv.IncomeAccountRef is None ):
        bag['IncomeAccount'] = "no account"
    else:
        bag['IncomeAccount'] = inv.IncomeAccountRef.name

    return(bag)
    

def main():
    global qbo_client
    qbo_client = qu.open_qbo_client()


    sqlbits = [];
       
    whereclause = ""
        
    
    ilist = pd.DataFrame( [ item2row(inv) for inv in item_iterable(whereclause=whereclause)])
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
