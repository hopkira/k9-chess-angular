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

# Use localhost websocket
address = "ws://127.0.0.1:1880/ws/ultrasonic"

# array of objects containing the sensor readings
sensor_readings = []

# manages the ws socket connection from this Controller to local node-RED server
class HarnessSocket(WebSocketClient) :

   def opened(self) :
      print "Ultrasonic test harness connected to node-RED server"

   def closed(self, code, reason=None) :
      print "Ultrasonic test harness disconnected from node-RED server: ", code, reason

def new_rotating_sensor(name, x, y, max, time, RANGE):
   """
   Simulates sensor readings from a rotating sensor

   Appends a number of readings according to a sweeep front to back of a
   rotating sensor (LIDAR on the real dog).  The angle covered by the sweep is
   dependent upon the speed of the dog - the faster the dog goes, the shorter
   the sweep and the fewer the readings.  This is to ensure that at higher speeds the
   sensors are looking sufficiently forward to avoid a head on collision.

   Keyword arguments:
   name - name of sensor
   x - x position of sensor
   y - y position of sensor
   max - maximum number of readings
   time - the actual time of the base reading
   RANGE - the maximum range of the sensor

   Cycle up and down the speed range of the dog (so number of readings varies) whilst
   separately cycling up and down the distance read from the sensors.
   """

def randomise(number):
    """
    Modify a provided number
    """
    number = number * random.uniform(0.5,1.5)
    return number

def createmsg(sensorname,distance):
    message = '{"type":"sensor","sensor":"'+sensorname+'","distance":"'+str(randomise(distance))+'"}'
    return message

"""
   initialise rotating sensors
   angle = -0.1745
   delta = 10/9*math.pi
   direction = 1
   dog_x = random.randint(-63,63)
   dog_y = random.randint(-63,63)
   max_sensor_readings = int(22-(math.hypot(dog_x, dog_y)/5))


      sensor_readings.append([name,x,y,angle,time,RANGE])
      angle = angle + (delta*direction)
      time = time + (0.02/max)
      if angle <= -0.1745:
         angle = -0.1745
         direction = direction * -1
      if angle >= math.pi:
         angle = math.pi
         direction = direction * -1
      readings = readings + 1
"""

try:
   ws = HarnessSocket(address)
   ws.connect()
   distance = 1.2
   sensorlist = ["left","bl_corner","tail","br_corner","right"]
   while (distance > 0.2):
       angle = 0
       while (angle < 360):
           index = 0
           message = '{"type":"sensor","sensor":"ultrasonic","angle":"'+str(angle)+'","distance":"'+str(randomise(distance))+'"}'
           ws.send(message)
           while (index < len(sensorlist)):
               ws.send(createmsg(sensorlist[index],distance));
               index = index + 1
           angle = angle + 10
           #message = json.dumps(message, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=(',', ':'), encoding="utf-8", default=None, sort_keys=False)
           time.sleep(0.12)
       distance = distance - 0.1
       #time.sleep(3)

except KeyboardInterrupt:
   ws.close()
   print "Exiting ultrasonic harness after closing socket."
