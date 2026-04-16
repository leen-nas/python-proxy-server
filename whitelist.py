#Author: Antonio
WHITELIST = {
    "example.com"
}


def is_allowed(host):
    if not WHITELIST:
        return True

    return host in WHITELIST