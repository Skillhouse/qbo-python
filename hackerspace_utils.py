
import copy
import os
import json
import re;
import pandas as pd;
import time;

debug = False

# What accounts do payments get recorded into?
payment_config="./payment_processing.json"

def get_paymentconfig():
    with open(payment_config) as cfgfile:
        return json.load(cfgfile)



# Out of the repo, natch.


secrets="../hackerspace-auth.json"
cache="../bearer-cache.json"

empty_cache = {
    'empty_cache' : True,
    'token' : "No token here",
    'refresh_token': "No refresh token here",
    'token_expires':   time.time(),
    'refresh_expires': time.time(),
    'token_expires_h':   "No token here",
    'refresh_expires_h': "No refresh token here",
}



def get_auth_bag_without_cache():
    with open(secrets) as authfile:
        bag1 = json.load(authfile)

    return(bag1)

def get_auth_bag():
    with open(secrets) as authfile:
        bag1 = json.load(authfile)

    bag1.update(get_bearer_cache())

    format_apiurl(bag1)
        
    return(bag1)


def format_apiurl(authbag):
    authbag['apiurl'] = authbag['apiurl_pattern'] .format(**authbag)

    



def get_bearer_cache(fail_ood=True,filename=cache):
    tempcache = ""

    if os.path.isfile(filename):
        with open(filename) as infile:
            tempcache= json.load(infile)
    else:
        tempcache = copy.deepcopy(empty_cache)
        # Set it already expired if the file is missing.

    secs_still_good = tempcache['token_expires'] - time.time()

    if(debug): print("# QBO auth token from cache good for {0:.1f} secs".format(secs_still_good))

    if(secs_still_good < 1 and fail_ood is True):
        raise ValueError('Token from cache no longer valid; expired {0}'.format(tempcache['token_expires_h']))
    
    return(tempcache)


def dump_bearer_cache(bearin,filename=cache):
    with open(filename,"w") as outfile:
        os.environ['TZ'] = 'EST+05EDT,M4.1.0,M10.5.0'
        time.tzset()
        json.dump(
            {
                'token' : bearin.accessToken,
                'refresh_token': bearin.refreshToken,
                'token_expires':   time.time() +bearin.accessTokenExpiry ,
                'refresh_expires': time.time() +bearin.refreshExpiry ,
                'token_expires_h':   time.ctime(time.time() +bearin.accessTokenExpiry) ,
                'refresh_expires_h': time.ctime(time.time() +bearin.refreshExpiry) ,

            },
            outfile,
            indent=4,
            sort_keys=True,
            )
   

def add_realm_to_bearer_cache(realm,filename=cache):
    with open(filename) as infile:
        tempcache= json.load(infile)

    tempcache['realm'] = tempcache['realm_id'] = realm

    with open(filename,"w") as outfile :
        json.dump(tempcache,outfile,indent=4,sort_keys=True)



        
stripepat = re.compile(r"^stripe: *(?P<custid>.+)$",re.MULTILINE)
    
def extract_stripecust_from_notes(innotes):
    result = stripepat.search(innotes)
    if result is None:
        return "[NO STRIPE CUST]"
    else:
        return result.group('custid')
    
    



csvin="../memberlist.csv"

cols_we_want = {
    "QBO ID"        : "QBOID",
    "Name"          : "name",
    "Email"         : 'email',
    "Phone Number"  : 'phone',
}


def all_cust_df(colmap=cols_we_want):

    
    df = pd.read_csv(csvin,header=1)

    df = df.loc[ df['ID'].notna()]

    df = df.filter(items=colmap.keys())
    
    df["QBO ID"] = df["QBO ID"].fillna(0).astype(int)
    
    df = df.rename(axis="columns",mapper=colmap)                    


    df = df.fillna("")

    
    return(df)


def active_cust_df(colmap=cols_we_want):
    if (debug): print("# Reading active customers")
    
    df = pd.read_csv(csvin,header=1)

    df = df.loc[ df['ID'].notna()]

    df = df.loc[df['STATUS'] == 'ACTIVE']

    df = df.filter(items=colmap.keys())

    df = df.rename(axis="columns",mapper=colmap)                    

    df = df.fillna("")

    df['QBOID'] = df['QBOID'].astype(int)

    return(df)





memberships={

    "REGULAR" : {
        "amount" : 35.00,
        "itemid" : 34
    },


    "STUDENT":  {
        "amount": 25.00
        ,"itemid" : 34

    }


    }

