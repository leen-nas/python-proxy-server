# CSC 430 - Computer Networks
# Cache manager ,  stores responses so we don't fetch the same thing twice
# Author: Lynn

import time
from config import CACHE_TIMEOUT, MAX_CACHE_SIZE

class CacheManager:
    def __init__(self):
        # url -> (response, time it was saved)
        self.cache = {}

    def get(self, url):
        if url in self.cache:
            response, timestamp = self.cache[url]
            # check if it's still fresh(current-when saved= less tahn 60 so fresh)
            if time.time() - timestamp < CACHE_TIMEOUT: 
                return response
            else:
                # expired, so remove it
                del self.cache[url]
        return None

    def set(self, url, response):
        # if cache is full remove the oldest entry first
        if len(self.cache) >= MAX_CACHE_SIZE:
            oldest = min(self.cache, key=lambda k: self.cache[k][1])
            del self.cache[oldest]
        self.cache[url] = (response, time.time())