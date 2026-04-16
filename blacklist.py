#Author: Antonio 
BLACKLIST = {
    "idi.com",
    "ads.google.com",
    "neverssl.com"
}

def is_blocked(host):
    # normalize host (VERY IMPORTANT)
    host = host.lower()
    host = host.replace("www.", "")
    host = host.split(":")[0]

    # check exact or subdomain match
    for blocked in BLACKLIST:
        if blocked in host:
            return True

    return False