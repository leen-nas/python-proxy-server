# =============================================================
# CSC 430 - Computer Networks | Spring 2025-2026
# Caching Proxy Server
# =============================================================
# Author: Lynn
# File: cache/cache_manager.py
# Description: Manages in-memory caching of HTTP responses.
#              Stores, retrieves, and invalidates cached data.
# =============================================================

import time
from config import CACHE_TIMEOUT, MAX_CACHE_SIZE

class CacheManager:
    def __init__(self):
        # Dictionary storing cached responses: {url: (response, timestamp)}
        self.cache = {}

    def get(self, url):
        # Check if URL exists in cache and hasn't expired
        if url in self.cache:
            response, timestamp = self.cache[url]
            if time.time() - timestamp < CACHE_TIMEOUT:
                return response  # Cache hit
            else:
                del self.cache[url]  # Expired, remove it
        return None  # Cache miss

    def set(self, url, response):
        # If cache is full, remove the oldest entry
        if len(self.cache) >= MAX_CACHE_SIZE:
            oldest = min(self.cache, key=lambda k: self.cache[k][1])
            del self.cache[oldest]
        # Store response with current timestamp
        self.cache[url] = (response, time.time())