#Author: Antonio 
BLACKLIST = {
    "idi.com",
    "httpforever.com",
    "foxnews.com",
    "neverssl.com"
}

def is_blocked(host):
    # normalize host (lowercase, remove www., strip port)
    host = host.lower()
    host = host.replace("www.", "")
    host = host.split(":")[0]

    # exact match or subdomain match
    for blocked in BLACKLIST:
        if host == blocked or host.endswith('.' + blocked):
            return True
    return False