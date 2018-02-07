# -*- coding: utf-8 -*-
#
# K9's Status Broadcaster using Redis
#
# authored by Richard Hopkins February 2018 for AoT Autonomy Team
#
# Licensed under The Unlicense, so free for public domain use
#
# This program creates a simple program that will repeatedly broadcast the
# state of the robot to a websocket

import json
import time
import threading
import math

print "Importing Redis library..."
import redis

from ws4py.client.threadedclient import WebSocketClient #enabling web sockets

#from k9secrets import K9PyStatusWS # gets the node-RED websocket address
#address = K9PyStatusWS

address="ws://localhost:1880/ws/k9"

class K9 :
    '''K9 state object
    '''
    def __init__(self) :
        # Connect to a local Redis server
        print "Connecting to local redis host"
        self.rdb = redis.Redis(host='127.0.0.1',port=6379)
    def get_sensor_state(self) :
        self.message=""
        # retrive the latest reading from every sensor and record
        # the message numbers in a temporary range ordered by angle
        self.sensor_keys = self.rdb.keys(pattern='sensor:*')
        # retrieve the list of all active sensors
        for self.sensor in self.sensor_keys:
            # for each sensor, retrieve get latest reading
            self.msg_key = self.rdb.lrange(self.sensor,0,0)
            # for each reading, retrieve the message text
            self.angle = self.rdb.hget(self.msg_key,'angle')
            # store the message by angle
            self.rdb.zadd('angle_range',self.angle,self.msg_key)
        self.ear_keys = self.rdb.keys(pattern='ear_')
        # retrieve all the readings from the ear sensors
        # and store them in a temporary range ordered by angle
        for self.ear in self.ear_keys:
            self.msg_keys = self.rdb.lrange(self.ear,1,-1)
            for self.msg in self.msg_keys
                self.angle = self.rdb.hget(self.msg,'angle')
                self.rdb.zadd('angle_range',self.angle,self.msg_key)
        # retrieve the list created
        self.msglist = self.rdb.zrangebyscore('angle_range',-math.pi,math.pi,withscores=False)
        for self.msg in self.msglist:
            self.message = self.message + self.rdb.hgetall(self.msg) + "\n"
        self.rdb.delete('angle_range')
        return self.message

    def get_toggle_state(self) :
        self.message=""
        self.toggle_keys = self.rdb.keys(pattern='state:*')
        for

class K9PythonController(WebSocketClient) :
    '''Create a websocket that sends an update every 200ms
    '''
    def send_status(self) :
       self.t = threading.Timer(0.2, self.send_status) # timer lasts 1 second
       self.t.start()  # stsrt timer
       self.message = self.k9.get_sensor_state()
       print self.message

    def opened(self) :
       print "K9 state broadcaster program connected to node-RED"
       self.k9 = K9()

    def closed(self, code, reason=None) :
       print "K9 state broadcaster program disconnected from node-RED", code, reason
       self.t.cancel()
       print "Status repeat cancelled"

try:
    ws = K9PythonController(address)
    ws.connect()
    time.sleep(1.0)
    ws.send_status()
    ws.run_forever()
except KeyboardInterrupt:
    ws.close()
    print "Exiting K9 state broadcaster after cleanup."
