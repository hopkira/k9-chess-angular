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

print "Importing Redis library..."
import redis
# Connect to a local Redis server
print "Connecting to local redis host"
r = redis.Redis(host='127.0.0.1',port=6379)

from ws4py.client.threadedclient import WebSocketClient #enabling web sockets

#from k9secrets import K9PyStatusWS # gets the node-RED websocket address
#address = K9PyStatusWS

address="ws://localhost:1880/ws/k9"

class K9PythonController(WebSocketClient) :

    def send_status(self) :
       self.t = threading.Timer(0.2, self.send_status) # timer lasts 1 second
       self.t.start()  # stsrt timer
       print "Status sent"

    def opened(self) :
       print "K9 state broadcaster program connected to node-RED"

    def closed(self, code, reason=None) :
       print "K9 state broadcaster program disconnected from node-RED", code, reason

    def cancel_status(self) :
       self.t.cancel()
       print "Status repeat cancelled"

try:
    ws = K9PythonController(address)
    ws.connect()
    ws.send_status()
    ws.run_forever()
except KeyboardInterrupt:
    ws.cancel_status()
    ws.close()
    print "Exiting K9 state broadcaster after cleanup."
