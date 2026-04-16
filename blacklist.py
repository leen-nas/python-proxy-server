#Author: Antonio
BLACKLIST = {
    "ads.google.com",
    "doubleclick.net",
    "neverssl.com"
}

def is_blocked(host):
    for blocked in BLACKLIST:
        if blocked in host:
            return True
    return False