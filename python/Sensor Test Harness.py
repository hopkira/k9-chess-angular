#
# K9 Python Sensor Data Test Harness
#
# authored by Richard Hopkins May 2017 for Autonomy Team
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

from ws4py.client.threadedclient import WebSocketClient #enabling web sockets

RANGE = 1200

# sim is a program wide flag to allow the program to run using localhost
# rather than the real robot environment
# this can be enabled by appending the word "test" to the command line

if ( len(sys.argv) > 1 ) :
   if ( sys.argv[1] == "test" ) :
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


test_num = 0

random.seed(42)

sensor_readings = []

while (test_num<100)
   dog_x = random.randint(-63,63)¶
   dog_y = random.randint(-63,63)
   start_time = time()
   step = 0
   max_sensor_readings = int(22-(math.hypot(dog_x, dog_y)/5))
   # initalise fixed sensors
   sensor_readings.append([name, x, y, angle, time, RANGE])
   sensor_readings.append([name, x, y, angle, time, RANGE])
   sensor_readings.append([name, x, y,angle, time, RANGE])
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
      
   while no_collision()
      message = "{"readings": ["
      for reading in sensor_readings:
         sensor_readings[reading][3] = new_dist(sensor_readings[reading][3], sensor_readings[reading][1],dog_x,dog_y)
         message = message + "big string of content" + ","
      message = message[less one character] + "]}"
   
   for reading in range(1,3):     
      sensor_readings[reading][3] = random.randint
   
   del sensor_readings[:]
   for sensors in range(0, 2):
      if sensor_readings[sensor][4]
   while 

def new_dist(old_dist,sensor_angle, dog_x,dog_y):
   # calculate components of x and y and modify distance accordingly
   # modify by +-10% up to a max of 1200 to simulate noise
   # calculate old_pos
   ang_mov =math.atan2(dog_y,dog_x)
   ang_diff = ang_mov - sensor_angle
   mag = math.hypot(dog_x, dog_y)
   new_dist = old_dist - (mag*cos(ang_diff)*random.randfloat(0.9,1.1))
   if new_dist > RANGE
      new_dist = RANGE
   return new_dist

def no_collision():
   min_dist = RANGE
   for reading in sensor_readings:
     if sensor_readings[reading][4] < min_dist
        min_dist = sensor_readings[reading][4]
   return (min_dist>127)

   

   for readings in range(0, max):
      sensor_readings.append([])





class Sensor:
   def __init__(self, name, direction) :
   self.name = name
   self.direction = direction
   print str(name) + " sensor created."
   
   def resetSensor(self):
      self.reading = random(902 MINUS A BIT)
        
   def getReading(self, time) :
      self.time = time
      self.reading = random(902 MINUS A BIT)

class RotatingSensor(Sensor):
   def __init__(self, name, direction) :
      Sensor.__init__(self, name, direction)
      
   def getReading(self,time) :
      do something more complex  

class SensorArray :
   def __init__(self) :
      print "Sensor array initialising"
      self.tailSensor = Sensor("name",x,y,min,max,angle)



class Scenario :
   def __init__(self)
      initialise array that defines sensors
      self.number = 0
   
   def startTest(self,number) :
     self.number = self.number + 1
     self.x_speed = random +-90
     self.y_speed = random +-90
     self.start = START TIME
     initialise each sensor
     while self.collision() == False
        self.getReadings()
        self.transmitReadings()
               
   def getReadings(self):
    calculate the new world by contracting each of the measures
    store in sensor array

   def transmitReadings(self):
    self.message = json.dumps({"type":"status","command":"update","left": self.left,"right": self.right,"lights": self.lights,"eyes": self.eyes,"hover": self.hover,"screen": self.screen, "motorctrl": self.motorctrl, "main_volt": self.main_volt, "brain_volt": self.brain_volt, "motor_l_amp": self.m1current, "motor_r_amp": self.m2current, "temp": self.temp }, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=(',', ': '), encoding="utf-8", default=None, sort_keys=False)
    ws.send(self.message)

   def getSensorData(self) :
      # retrieves status of motors and lights
      # lights are part of the k9 state object anyway
      

# manages the ws socket connection from this Controller to local node-RED server
class HarnessSocket(WebSocketClient) :

   def opened(self) :
      print "Test harness connected to node-RED server"

   def closed(self, code, reason=None) :
      print "Test harness disconnected from node-RED server: ", code, reason


try:
   ws = HarnessSocket(address)
   ws.connect()
   test = Scenario()
   while test.number < 100
      test.startTest()       
   # ws.run_forever()
except KeyboardInterrupt:
   ws.close()
   print "Exiting harness after closing socket."
