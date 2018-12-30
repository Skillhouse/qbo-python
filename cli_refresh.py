#!/usr/bin/env python
''' cli_refresh -- update web tokens, from a CLI. 

Usage: 
  cli_refresh [options]


Options:
  --debug                  Print debugging output. [default: False]



'''

from docopt import docopt
import requests
import base64
import json
import random
import os
import sys

from jose import jwk
from datetime import datetime

# Misbegotten grafting of django app into our CLI thing.
sys.path.insert(0, "./djangoapp")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OAuth2DjangoSampleApp.settings")

from sampleAppOAuth2.models import Bearer
from django.core.wsgi import get_wsgi_application
from django.conf import settings

# application = get_wsgi_application()


import hackerspace_utils as hu




def stringToBase64(s):  return base64.b64encode(bytes(s, 'utf-8')).decode()


# If this were less totally idiosyncratic, might wind it into one
# of the other util scripts.


def getBearerTokenFromRefreshToken(refresh_Token):

    token_endpoint = 'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer'

    auth_header = 'Basic ' + stringToBase64(settings.CLIENT_ID + ':' + settings.CLIENT_SECRET)
    headers = {'Accept': 'application/json', 'content-type': 'application/x-www-form-urlencoded',  'Authorization': auth_header}
    payload = {'refresh_token': refresh_Token, 'grant_type': 'refresh_token'  }

    r = requests.post(token_endpoint, data=payload, headers=headers)
    bearer_raw = json.loads(r.text)

    if 'id_token' in bearer_raw:
        idToken = bearer_raw['id_token']
    else:
        idToken = None

    return Bearer(bearer_raw['x_refresh_token_expires_in'], bearer_raw['access_token'], bearer_raw['token_type'], bearer_raw['refresh_token'], bearer_raw['expires_in'], idToken=idToken)



def main():

    authbag = hu.get_auth_bag()

    tempcache = hu.get_bearer_cache(fail_ood=False)

    if tempcache['empty_cache'] is True:
        tempcache = {} 

    authbag.update(tempcache)
        
    newbearer = getBearerTokenFromRefreshToken(authbag['refresh_token'])
    
    hu.dump_bearer_cache(newbearer)

    print("New token: \n")
    
    authbag = hu.get_bearer_cache(fail_ood=False)
    
    print (json.dumps(authbag,indent=4,sort_keys=True))
   


    
if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')

    debug = arguments['--debug']

    if (debug):
        print(arguments)
        hu.debug=True

    main()

