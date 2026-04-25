# CSC 430 - Computer Networks
# Config - all the settings in one place so they're easy to change
# Author: Leen

HOST = '0.0.0.0'          #listen & accept form all
PORT = 8888               #send requests to this port
BUFFER_SIZE = 4096        #each chunk is 4096 bytes
CACHE_TIMEOUT = 60        #cached repsonse expire after 60sec
MAX_CACHE_SIZE = 100      #max responses stored in memory 
                        