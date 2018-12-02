

import json



# Out of the repo, natch.
secrets="../hackerspace-auth.json"

def get_auth_bag():
    with open(secrets) as authfile:
        return json.load(authfile)




