#!/usr/bin/env python 
"""listpayments -- 

List payments from QBO.



Usage:
  listpayments.py  [options]

Options:
  --debug                  Print debugging output. [default: False]

  --starting=<DATE>        Payments on or after this date. [default: the first]
  --ending=<DATE>          Payments before (NOT on) this date. [default: today]

  --custid <id[,id...]>    List for specified QBO IDs. 

  --and-then-delete        Remove the payments revealed by this query.

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
from quickbooks.objects import Payment
from quickbooks.batch import batch_delete



import qbo_utils as qu

#
# Still thinking about how to parameterize this.  While it's clumsy,
# it'll stay broken out here.
#

qbo_client = None

def payment_iterable(whereclause="",**kwargs):
    reps = 0
    yielded = 0
    
    while (True):
        
        payments = Payment.where(whereclause,
            qb=qbo_client,
            max_results=100,
            start_position=yielded+1,
            **kwargs
        )
        reps += 1

        if len(payments) == 0:
            return

        for item in payments:
            yielded += 1
            yield(item)



def payment2row(inv):
    bag = {
        'TxnDate'   : inv.TxnDate,
        'custid'    : inv.CustomerRef.value,
        'custname'  : inv.CustomerRef.name,
        'TotalAmt'  : inv.TotalAmt,
        'Id'        : inv.Id,
    }
    return(bag)
    

def main():
    global qbo_client
    qbo_client = qu.open_qbo_client()


    sqlbits = [];
    sqlbits.append("TxnDate >= '{--starting}'".format(**arguments))
    sqlbits.append("TxnDate < '{--ending}' ".format(**arguments))
       
    if not arguments['--custid'] is None:
        custs = "CustomerRef in (" + ",".join("'{0}'".format(str(i)) for i in arguments['--custid']) + ")"
        sqlbits.append(custs)

    whereclause = " and ".join(sqlbits)
        
    
    ilist = pd.DataFrame( [ payment2row(inv) for inv in payment_iterable(whereclause=whereclause)])
    if (len(ilist) == 0 ) :
        print("No matches for your query: \n---\n{0}\n---\n".format(whereclause))
        sys.exit()

    ilist['Id'] = ilist['Id'].astype(int)
    ilist['custid'] = ilist['custid'].astype(int)
    print(ilist)

    bag = {}
    bag['icount'] = len(ilist)
    
    if (arguments['--and-then-delete'] is True):
        if ( arguments['--doit'] is True):
            print("Batch deletion beginning.  Max batch is 100.")
            payments = Payment.where(whereclause,qb=qbo_client)
            results = batch_delete(payments,qb=qbo_client)
            
            if len(results.faults) > 0:
                print(results.faults)
            else:
                bag['scount'] = len(results.successes)
                print("No faults returned; {scount} of {icount} removed.".format(**bag))

                
                

                
                
                
        else:
            print("\nDeletion requested but not confirmed.  --doit if you mean it. \n")


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']

    if (arguments['--custid']):
        arguments['--custid'] = [ int(x) for x in arguments['--custid'].split(",")]
 

    if ( arguments['--starting'] == "the first" ) :
        arguments['--starting'] = dateparser.parse("{0} days ago".format(dateparser.parse("today").day -1 )).date().isoformat()
    else:
        arguments['--starting'] = dateparser.parse(arguments['--starting']).date().isoformat()

    arguments['--ending'] =  dateparser.parse(arguments['--ending']).date().isoformat()

    
        

    if (debug):
        qu.debug=True
        hu.debug=True
        print(arguments)

    main()
