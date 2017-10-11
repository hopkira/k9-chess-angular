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

random.seed(42)

sim=False

total_start_time = time.time()

# RANGE represents the maximum range of the sensors in mm
RANGE = 1200

# COLLISION represents the guaranteed minimum distance in mm
COLLISION = 127

# max_tests is the number of tests to be run, default is 200
max_tests = 200

# array of objects containing the sensor readings
sensor_readings = []

total=0

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
   else:
      max_tests = int(sys.argv[1])

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
   address = "ws://127.0.0.1:1880/ws/sensors"

def do_tests(max_tests):
   """
   Intialises sensors and sends readings to node-RED until collision occurs

   Keyword arguments:
   max_tests - number of collisions to simulate
   """
   global total
   test_num = 0
   while (test_num < max_tests):
      del sensor_readings[:]
      dog_x = random.randint(-63,63)
      dog_y = random.randint(-63,63)
      start_time = time.time()
      step = 0
      max_sensor_readings = int(22-(math.hypot(dog_x, dog_y)/5))
      # initalise sensors
      new_static_sensor("left", -143, 95, math.pi*1/2, start_time, RANGE)
      new_static_sensor("bl_corner", -190, 48, math.pi*3/4, start_time, RANGE)
      new_static_sensor("tail", -237, 0, math.pi, start_time, RANGE)
      new_static_sensor("br_corner", -190, -48, math.pi*-3/4, start_time, RANGE)
      new_static_sensor("right", -143, -95, math.pi*-1/2, start_time, RANGE)
      new_rotating_sensor("l_ear", 343, 42, max_sensor_readings, start_time, RANGE)
      new_rotating_sensor("r_ear", 343, -42, max_sensor_readings,start_time, RANGE)
      #print str(sensor_readings)
      # change the readings until collision occurs
      while no_collision():
         #message = '{"readings'+ str(test_num) +'":{'
         index = 0
         while (index < len(sensor_readings)):
            sensor_readings[index][5] = new_dist(sensor_readings[index][5], sensor_readings[index][3], dog_x, dog_y)
            message = '{"sensor":"' + sensor_readings[index][0] + '","x":' + str(sensor_readings[index][1]) + ',"y":' + str(sensor_readings[index][2]) + ',"angle":' + str(sensor_readings[index][3]) + ',"time":' + str(sensor_readings[index][4]) + ',"dist":' + str(sensor_readings[index][5]) + "}"
            index = index +1
            #message = json.dumps(message, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=(',', ':'), encoding="utf-8", default=None, sort_keys=False)
            ws.send(message)
            time.sleep(0.1)
            total=total+1
            #print str(message)
         step = step + 1
      test_num = test_num + 1

def new_static_sensor(name, x, y, angle, time, RANGE):
   """
   Simulates a sensor reading from a static sensor

   Keyword arguments:
   name - name of sensor
   x - x position of sensor
   y - y position of sensor
   angle - direction sensor is facing
   time - the actual time of the base reading
   RANGE - the maximum range of the sensor
   """
   index = len(sensor_readings)
   sensor_readings.append([name,x,y,angle,time,RANGE])

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
   """
   # initialise rotating sensors
   angle = -0.1745
   delta = 10/9*math.pi
   direction = 1
   readings = 0
   while readings < max:
      index = len(sensor_readings)
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

def new_dist(old_dist,sensor_angle, dog_x,dog_y):
   """
   Calculate how motion and noise will change sensor readings

   The function returns the new distance sensed; this his includes
   addding 10% of simulated noise to the readings

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
   new_dist = old_dist - (mag*math.cos(ang_diff)*random.uniform(0.9,1.1))
   # limit the sensor reading to its maximum but no more   hji
   if new_dist > RANGE:
      new_dist = RANGE
   return new_dist

def no_collision():
   """Detect a collision by calculating the minimum sensor distance for all sensors"""
   min_dist = RANGE
   #print str(len(sensor_readings))
   index = 0
   while (index < len(sensor_readings)):
      #print index
      #print sensor_readings[index][5]
      if sensor_readings[index][5] < min_dist:
         min_dist = sensor_readings[index][5]
      index = index + 1
   return (min_dist>COLLISION)


# manages the ws socket connection from this Controller to local node-RED server
class HarnessSocket(WebSocketClient) :

   def opened(self) :
      print "Test harness connected to node-RED server"

   def closed(self, code, reason=None) :
      print "Test harness disconnected from node-RED server: ", code, reason

try:
   ws = HarnessSocket(address)
   ws.connect()
   do_tests(max_tests)
   print str(total) + " sensor messages transmitted in " + str(int(time.time()-total_start_time)) + " seconds"
except KeyboardInterrupt:
   ws.close()
   print "Exiting harness after closing socket."
