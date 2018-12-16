

import json
import re;
import pandas as pd;


debug = False

# What accounts do payments get recorded into?
payment_config="./payment_processing.json"

def get_paymentconfig():
    with open(payment_config) as cfgfile:
        return json.load(cfgfile)


# Out of the repo, natch.
secrets="../hackerspace-auth.json"

def get_auth_bag():
    with open(secrets) as authfile:
        return json.load(authfile)


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

    df = df.rename(axis="columns",mapper=colmap)                    

    df = df.fillna("")

    df['QBOID'] = df['QBOID'].astype(int)

    
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
        "itemid" : 24
    },


    "STUDENT":  {
        "amount": 25.00
        ,"itemid" : 25

    }


    }

