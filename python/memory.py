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
import time

json_data = '{"message":{"type":"sensor","name":"touch_back","angle":"999"}}';

print "Importing Redis library..."
import redis
# Connect to a local Redis server
print "Connecting to local redis host"
r = redis.Redis(host='127.0.0.1',port=6379)


def storeState(key,value):
    ''' Stores the value of a received key and the time it was stored as well as preserving the previous value
    '''
    old_value = r.get(str(key) + ":now")
    r.set(str(key) + ":old", old_value )
    old_value = r.get(str(key) + ":time:now")
    r.set(str(key) + ":time:old", old_value)
    r.set(str(key) + ":now",str(value))
    r.set(str(key) + ":time:now",str(time.time()))

def retrieveState(key):
    '''Retrieves the last version of a desired key
    '''
    return r.get(str(key) + ":now")

def getMsgKey():
    '''Uses redis to create a unique message key by incrementing message_num
    '''
    msg_key = "message_"+str(r.incr("message_num",amount=1))
    return msg_key

def storeSensorReading(name,reading,angle):
    '''Stores a sensor reading as a JSON string, compatible with other sensor readings
    '''
    json_data = '{"type":"sensor","sensor":"'+str(name)+'","distance":"'+str(reading)+'","angle":"'+str(angle)+'"}'
    storeSensorMessage(str(json_data))

def storeSensorMessage(json_data):
    '''Stores a JSON string formatted sensor reading message
    '''
    # Parse message into dictionary of name value pairs
    message = {}
    message = json.loads(json_data)
    print message
    print len(message)
    msg_key = getMsgKey()
    # Create a transactional pipeline to store new message, this will be closed
    # and committed by the pipe.execute() command
    pipe = r.pipeline(transaction=True)
    # Store the whole of the message as a hash value
    pipe.hmset(msg_key,message)
    # Expire all messages after 10 seconds
    pipe.expire(msg_key,10)
    # For each of the message generating devices e.g. sensors, create a list
    # where the most recent element is at the left of the list
    pipe.lpush(message["sensor"],msg_key)
    # Ensure that the list for each device doesn't get any longer than 15 messages so
    # stuff will fall of the right hand end of the list
    pipe.ltrim(message["sensor"],0,15)
    # Execute all of the above as part of a single transactional interaction with the
    # Redis server
    pipe.execute()

def retrieveSensorMessage(sensor):
    '''Retrieves the last message stored for a sensor
    '''
    msg_key=r.lrange(sensor,0,0)
    msg = r.hmget(msg_key)
    return msg

def retrieveSensorReading(sensor):
    '''Retrieves the last values stored for a sensor
    '''
    message = json.loads(retrieveSensorMessage(sensor))
    return message

def retriveSensorArray():
    '''list of sensors'''

storeState("left:speed",0)
storeState("right:speed",0)
