# -*- coding: utf-8 -*-
#
# K9's Short Term Memory using Redis
#
# authored by Richard Hopkins January 2017 for AoT Autonomy Team
#
# Licensed under The Unlicense, so free for public domain use
#
# This program provides K9 with a short term memory that can recall
# all internal messages from sensors, motors, browser commands etc.
# for the last 10 seconds.  It also enables this history of messages to
# be quickly retrieved on a per sensor basis

import json

json_data = '{"message":{"type":"sensor","name":"touch_back","angle":"999"}}';

print "Importing Redis library..."
import redis
# Connect to a local Redis server
r = redis.Redis(host='127.0.0.1',port=6379)

# Parse message into dictionary of name value pairs
message = json.loads(json_data)
print message

def storeMessage(message):
    # Create next unique message key based on incrementing message_num
    msg_key = "message_"+str(r.incr("message_num",amount=1))
    print msg_key
    # Create a transactional pipeline to store new message, this will be closed
    # and committed by the pipe.execute() command
    pipe = r.pipeline(transaction=True)
    # Store the whole of the message as a hash value
    pipe.hmset(msg_key,message)
    # Expire all messages after 10 seconds
    pipe.expire(msg_key,10)
    # For each of the message generating devices e.g. sensors, create a list
    # where the most recent element is at the left of the list
    pipe.lpush(message.name,msg_key)
    # Ensure that the list for each device doesn't get any longer than 15 messages so
    # stuff will fall of the right hand end of the list
    pipe.ltrim(message.name,0,15)
    # Execute all of the above as part of a single transactional interaction with the
    # Redis server
    pipe.execute()

def getLastMessage(sensor):
    msg_key=r.lrange(sensor,0,0)
    msg = r.hmget(msg_key)
    return msg

def getMessages(sensor,number):
    msg_keys=r.lrange(sensor,0,number)
    msg = ""
    for s in [msg_keys]:
        msg = msg + r.hmget(s)
    return msg

x = storeMessage(message)
print x
