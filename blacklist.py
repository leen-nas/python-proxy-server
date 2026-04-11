# Placeholder - Author: Antonio
BLACKLIST = {"ads.google.com", "doubleclick.net", "neverssl.com"}

def is_blocked(host):
    return host in BLACKLIST