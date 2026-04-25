# Author: Antonio
import time
from config import CACHE_TIMEOUT, MAX_CACHE_SIZE


class CacheEntry:
    def __init__(self, data):
        self.data = data
        self.timestamp = time.time()


class CacheManager:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            entry = self.cache[key]

            # check expiration
            if time.time() - entry.timestamp < CACHE_TIMEOUT:
                return entry.data
            else:
                # expired → remove
                del self.cache[key]

        return None

    def set(self, key, value):
        # limit cache size
        if len(self.cache) >= MAX_CACHE_SIZE:
            # remove oldest item
            oldest_key = min(self.cache, key=lambda k: self.cache[k].timestamp)
            del self.cache[oldest_key]

        self.cache[key] = CacheEntry(value)

    def clear(self):
        self.cache.clear()

    def stats(self):
        return {
            "size": len(self.cache),
            "max_size": MAX_CACHE_SIZE
        }