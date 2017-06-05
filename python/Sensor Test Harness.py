# -*- coding: utf-8 -*-
#
# K9 Python Sensor Data Test Harness
#
# authored by Richard Hopkins May 2017 for AoT Autonomy Team
#
# Licensed under a Creative Commons Attribution-NonCommercial 4.0 International License.
#
# This program pretends to be seven sensors to enable quick evaluation tuning and
# prototyping of a collision detection algorithm for K9
#
# It will generate a set of sensor data every 20ms and transmit that to
# a websocket as a JSON string. The initial destination is assumed to be node-RED,
# but it could be any runtime platform that supports websockets.
#
# The sensor data will always begin at the extremities of the sensors and then 
# modified in line with the expected movement of the robot and a random element.
# Once it is clear a collision has occurred the harness will reset with another
# scenario.  Each message will have an identifier enabling the message to be correlated
# with any detected collision
#
import sys     # allows for command line to be interpreted
import json    # enables creation of JSON strings
import os      # enables access to environment variables
import math    # import maths operations
import random  # import random numbers
import time    # enable sleep function

sys.path.append('/home/pi') # persistent import directory for K9 secrets

from ws4py.client.threadedclient import WebSocketClient # enabling web sockets

# RANGE represents the maximum range of the sensors in mm
RANGE = 1200

# num_tests is the number of tests to be run, default is 200
num_tests = 200

# sim is a program wide flag to allow the program to run using localhost
# rather than the real robot environment
# this can be enabled by appending the word "local" to the command line
#
# usage: harness [num_tests...] [<local>]
#   options:
#       num_tests   Changes the number of tests that are run, defaults to 200
#       local       Points the websocket to the localhost
#
#  e.g. "harness 350 local"

if ( len(sys.argv) > 1 ) :
   if ( sys.argv[1] == "local" ) :
      sim = True
      print "Executing in local mode" # let the user know they are in sim mode
   else num_tests = int(sys.argv[1])

if ( len(sys.argv) > 2 ) :
   if ( sys.argv[2] == "local" ) :
      sim = True
      print "Executing in local mode" # let the user know they are in sim mode

# If running for real initialise remote socket
if not sim :
   from k9secrets import K9PyContWS # gets the node-RED websocket address
   address = K9PyContWS
   print "Node-RED address is: " + str(address)
else :
   # otherwise use local host as node-RED server
   address = "ws://127.0.0.1:1880/ws/k9"

def do_tests(num_tests):
   test_num = 0
   sensor_readings = []
   while (test_num<100)
      dog_x = random.randint(-63,63)¶
      dog_y = random.randint(-63,63)
      start_time = time()
      step = 0
      max_sensor_readings = int(22-(math.hypot(dog_x, dog_y)/5))
      # initalise sensors
      new_static_sensor(name, x, y, angle, time, RANGE)
      new_static_sensor(name, x, y, angle, time, RANGE)
      new_static_sensor(name, x, y, angle, time, RANGE)
      new_rotating_sensor(name, x, y, angle, time, RANGE)
      new_rotating_sensor(name, x, y, angle, time, RANGE)
      # change the readings until collision occurs
      while no_collision()
         message = '{"readings": ['
         for reading in sensor_readings:
            sensor_readings[reading][3] = new_dist(sensor_readings[reading][3]
            message = message + "sensor:" + sensor_readings[reading][0] + ",x:" + dog_x + ",y:" + dog_y + ",angle:" + sensor_readings[reading][3] + ",time:" + sensor_readings[reading][4] + ",dist:" + sensor_readings[reading][5] + ","
         message = message[:-1] + "]}"
         print message
         ws.send(message)
         message = json.dumps(message, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=(',', ':'), encoding="utf-8", default=None, sort_keys=False)
      print "************* COLLISION **************"

def new_static_sensor(name, x, y, angle, time, RANGE):
   sensor_readings.append([name, x, y, angle, time, RANGE])
                                                   
def new_rotating_sensor(name, x, y, angle, time, RANGE):
   # initialise rotating sensors
   angle = -0.1745
   delta = 10/9*math.PI()
   direction = 1
   for reading in max_sensor_readings:
      sensor_readings.append([name, x, y, angle, time, RANGE])
      angle = angle + (delta*direction)
      time = time + (20/max_sensor-readings)
      if angle <= -0.1745
         angle = -0.1745
         direction = direction * -1
      if angle >= math.PI()
         angle = math.PI()
         direction = direction * -1

def new_dist(old_dist,sensor_angle, dog_x,dog_y):
   """Calculate how the dog's motion will change sensor readings and return new distance
   This includes addding an 10% of simulated noise to the readings
   
   Keyword arguments:
   old_dist -- the existing sensor reading
   sensor_angle -- the direction the sensor is facing
   dog_x -- the x component of the dog's motion
   dog_y -- the y component of the dog's motion
   """
   # calculate direction of dog's movement
   ang_mov =math.atan2(dog_y,dog_x)
   # calcualte difference between movement and sensor angle
   ang_diff = ang_mov - sensor_angle
   # calculate speed of movement using Pythagoras Theorem                                               
   mag = math.hypot(dog_x, dog_y)
   # calculate new distance and multiply by a noise factor
   new_dist = old_dist - (mag*cos(ang_diff)*random.randfloat(0.9,1.1))
   # limit the sensor reading to its maximum but no more
   if new_dist > RANGE
      new_dist = RANGE
   return new_dist

def no_collision():
   """ Detect a collision by calculating the minimum sensor distance for all sensors"""
   min_dist = RANGE
   for reading in sensor_readings:
     if sensor_readings[reading][4] < min_dist
        min_dist = sensor_readings[reading][4]
   return (min_dist>127)   

# manages the ws socket connection from this Controller to local node-RED server
class HarnessSocket(WebSocketClient) :

   def opened(self) :
      print "Test harness connected to node-RED server"

   def closed(self, code, reason=None) :
      print "Test harness disconnected from node-RED server: ", code, reason

random.seed(42)

try:
   ws = HarnessSocket(address)
   ws.connect()
   do_tests(num_tests)          
   ws.run_forever()
except KeyboardInterrupt:
   ws.close()
   print "Exiting harness after closing socket."
