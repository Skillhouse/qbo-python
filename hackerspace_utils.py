

import json
import re;



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
    
    
