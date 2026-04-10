# Placeholder - Author: Antonio
BLACKLIST = {"ads.google.com", "doubleclick.net"}

def is_blocked(host):
    return host in BLACKLIST