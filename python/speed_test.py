import sys     # allows for command line to be interpreted
import json    # enables creation of JSON strings
import os      # enables access to environment variables
import math    # import maths operations
import random  # import random numbers
import time    # enable sleep function

print "Importing Redis library..."
import redis
# Connect to a local Redis server
r = redis.Redis(host='127.0.0.1',port=6379)

def my_range(start, end, step):
    while start <= end:
        yield start
        start += step

for speed in my_range (-10.0,100.0,1):
    r.set("left",str(speed))
    r.set("right",str(speed))
    print ("Speed set to:" + str(speed))
    time.sleep(1.0)
