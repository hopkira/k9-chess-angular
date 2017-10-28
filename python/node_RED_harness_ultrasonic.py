# -*- coding: utf-8 -*-
#
# K9 Python Sensor Ultrasonic Data Test Harness
#
# authored by Richard Hopkins May 2017 for AoT Autonomy Team
#
# Licensed under The Unlicense, so free for public domain use
#
# This program pretends to be the output of the neural net
#
# It will generate a set of sensor data every 120ms and transmit that to
# a websocket as a JSON string. The initial destination is assumed to be node-RED,
# but it could be any runtime platform that supports websockets.
#
#
import sys     # allows for command line to be interpreted
import json    # enables creation of JSON strings
import os      # enables access to environment variables
import math    # import maths operations
import random  # import random numbers
import time    # enable sleep function

sys.path.append('/home/pi') # persistent import directory for K9 secrets

from ws4py.client.threadedclient import WebSocketClient # enabling web sockets

random.seed(42)

# RANGE represents the maximum range of the sensors in mm
RANGE = 1200

address = "ws://127.0.0.1:1880/ws/ultrasonic"

# manages the ws socket connection from this Controller to local node-RED server
class HarnessSocket(WebSocketClient) :

   def opened(self) :
      print "Ultrasonic test harness connected to node-RED server"

   def closed(self, code, reason=None) :
      print "Ultrasonic test harness disconnected from node-RED server: ", code, reason

try:
   ws = HarnessSocket(address)
   ws.connect()
   distance =1.2
   while (distance > 0.2):
       angle = 0
       while (angle < 360):
           message = '{"type":"sensor","sensor":"ultrasonic","angle":"'+str(angle)+'","distance":"'+str(distance)+'"}'
           ws.send(message)
           message = '{"type":"sensor","sensor":"left","distance":"'+str(distance)+'"}'
           ws.send(message)
           message = '{"type":"sensor","sensor":"bl_corner","distance":"'+str(distance)+'"}'
           ws.send(message)
           message = '{"type":"sensor","sensor":"tail","distance":"'+str(distance)+'"}'
           ws.send(message)
           message = '{"type":"sensor","sensor":"br_corner","distance":"'+str(distance)+'"}'
           ws.send(message)
           message = '{"type":"sensor","sensor":"right","distance":"'+str(distance)+'"}'
           ws.send(message)
           angle = angle + 10
           #message = json.dumps(message, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=(',', ':'), encoding="utf-8", default=None, sort_keys=False)
           time.sleep(0.12)
       distance = distance - 0.1
       #time.sleep(3)

except KeyboardInterrupt:
   ws.close()
   print "Exiting ultrasonic harness after closing socket."
