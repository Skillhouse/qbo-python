#!/usr/bin/env python 
''' listinvoicesforcust -- list invoices for a hackerspace cust.

Usage: 
  listcust <custid> [options]


Dump a simple list of invoices for a customer.


Arguments:
  <custid>                QBO customer ID of the customer.  Use listcust to find. 

Options:
  --debug                  Print debugging output. [default: False]



'''

from docopt import docopt
import requests
import json
import hackerspace_utils as hu




def main():
    authbag = hu.get_auth_bag()


    route="query"

    url = "/".join([authbag['apiurl'],route])

    querystring = {"minorversion":"14"}

    payload="select * from Invoice where CustomerRef = '{custid}'  startposition 1 maxresults 5".format(custid=arguments['<custid>'])

    Token = authbag['token'];

    headers = {
        'Accept': "application/json",
        'Content-Type': "application/text",
        'Authorization': "Bearer "+Token,
        'Cache-Control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    
    resj = json.loads(response.text);
    
#    print(json.dumps(resj,indent=4,sort_keys=True))
    
    # import pdb; pdb.set_trace()

    distillate = { inv['Id']:
                   {
                       'custid':inv['CustomerRef']['value'],
                       'custname':inv['CustomerRef']['name'],
                       'TxnDate':inv['TxnDate'],
                       'Amount':inv['TotalAmt'],
                       'Id': inv['Id'],
                   }
                   for inv in resj['QueryResponse']['Invoice'] }


    print ( "\n".join(["{TxnDate}: #{Id} for {Amount} ".format(**dis) for dis in distillate.values()   ] ) ) 



#     print (json.dumps(distillate,sort_keys=True,indent=4))



    
    


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']

    if (debug):
        print(arguments)
        hu.debug=True

    main()
