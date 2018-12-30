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


qbo_client = None
session_manager = None

def cust_iterable():
    bitesize = 100
    reps=0
    yielded = 0
    
    while (True):

        customers = Customer.filter(Active=True,
                                    qb=qbo_client,
                                    max_results=bitesize,
                                    start_position=yielded+1)
        reps += 1

        if len(customers) == 0:
            return

        for item in customers:
            yielded += 1
            yield(item)
    


def main():
    global session_manager
    global qbo_client

    authbag = hu.get_auth_bag()

    session_manager = Oauth2SessionManager(
        client_id=authbag['realm'],
        client_secret=authbag['secret'],
        access_token=authbag['token'],
        refresh_token=authbag['refresh_token'],
        base_url=authbag['redirect'],
    )

    qbo_client = QuickBooks(
        sandbox=True,
        session_manager=session_manager,
        company_id=authbag['realm']
    )
    
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

    if (debug):
        print(arguments)
        hu.debug=True

    main()

