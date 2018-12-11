#!/usr/bin/env python
''' listcust -- list hackerspaces QBO customers.

Usage: 
  listcust [options]


Dump a simple scan of the QBO customers, in CSV.



Options:
  --debug                  Print debugging output. [default: False]



'''


from docopt import docopt
import requests
import json
import hackerspace_utils as hu
import qbo_utils as qu

from quickbooks import Oauth2SessionManager
from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer
from quickbooks.objects import Account


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

        customers = Customer.filter(Active=True,
                                    qb=client,
                                    max_results=100,
                                    start_position=yielded+1)
        reps += 1

        if len(customers) == 0:
            return

        for item in customers:
            if (debug): print("Reps: {0}.  Yielded: {1} bitecount: {2}".format(reps,yielded,len(customers)))
        

            yielded += 1
            yield(item)
    



def main():

    
    for customer in cust_iterable():

        cd = customer.to_dict()

        try:
            cd['email'] = cd['PrimaryEmailAddr']['Address']
        except TypeError:
            cd['email'] = ""

        print("{Id},{DisplayName},{email}".format(**cd))
        
    
    


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']

#    if (debug): api_functions.debug=True
    if (debug): print(arguments)

    main()

