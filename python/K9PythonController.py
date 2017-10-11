#
# K9 Python Controller
#
# authored by Richard Hopkins, October 2017
#
# Licensed under a Creative Commons Attribution-NonCommercial 4.0 International License.
#
# This program performs receives two different command strings
# of type 'navigation' routed from a local node-RED instance.
#
# In response to the 'browser' command (a heartbeat every 250ms generated in the brower)
# it will respond with status information about the driving motors and other information
# e.g. status of lights.  Node-RED will then route this information to the end user browser.
#
# In response to the 'motors' command, the controller will calculate the respective motor speeds
# and send a message to the Roboclaw to move K9 at that speed and direction for 30 cm.
#
import sys     # allows for command line to be interpreted
import json    # enables creation of JSON strings
import os      # enables access to environment variables
import math    # import maths operations
import random  # import random numbers
import time    # enable sleep function

sys.path.append('/home/pi') # persistent import directory for K9 secrets
sys.path.append('/home/pi/Adafruit_Python_PCA9685/Adafruit_PCA9685') # persistent directory for Adafruit driver

from ws4py.client.threadedclient import WebSocketClient #enabling web sockets

sim = False # by default run as a real motor controller
m1_qpps = 708
m2_qpps = 720

# sim is a program wide flag to allow the program to run without the Roboclaw
# and without access to the Raspberry Pi GPIO ports
# this can be enabled by appending the word "test" to the command line

if ( len(sys.argv) > 1 ) :
   if ( sys.argv[1] == "test" ) :
      sim = True
      print "Executing in simulation mode" # let the user know they are in sim mode

# If running for real initialise remote socket, roboclaw driver and GPIO
if not sim :
   print "Importing servo driver library..."
   import Adafruit_PCA9685 # enable control of devices
   from k9secrets import K9PyContWS # gets the node-RED websocket address
   address = K9PyContWS
   print "Node-RED address is: " + str(address)
   # Initialise the roboclaw motorcontroller
   print "Initialising roboclaw driver..."
   from roboclaw import Roboclaw
   rc = Roboclaw("/dev/roboclaw",115200)
   rc.Open()
   rc_address = 0x80
   # Get roboclaw version to test if is attached
   version = rc.ReadVersion(rc_address)
   if version[0]==False:
      print "Roboclaw get version failed"
      sys.exit()
   else:
      print repr(version[1])
      # Set PID variables to those required by K9
      rc.SetM1VelocityPID(rc_address,3000,300,0,m1_qpps)
      rc.SetM2VelocityPID(rc_address,3000,300,0,m2_qpps)
      # Zero the motor encoders
      rc.ResetEncoders(rc_address)
      print "PID variables set on roboclaw"
   import RPi.GPIO as GPIO # enables manipulation of GPIO ports
   GPIO.setmode(GPIO.BOARD) # use board numbers rather than BCM numbers
   GPIO.setwarnings(False) # remove duplication warnings
   chan_list = [11,13]    # GPIO channels to initialise and use
   GPIO.setup(chan_list, GPIO.IN) # set GPIO to low at initialise
else :
   # otherwise use local host as node-RED server and don't initialise GPIO or Roboclaw
   address = "ws://127.0.0.1:1880/ws/motors"

class Motor :
   def __init__(self,name,QPPS) :
      self.name = name
      self.QPPS = QPPS/100.0
      print str(name) + " motor object instantiated."
      self.speed = 0.0
      self.target = 0.0

   def calculateTargetSpeed(self,reqmotorspeed,reqsteering,motorctrl) :
      self.reqmotorspeed = reqmotorspeed
      self.reqsteering = reqsteering
      self.motorctrl = motorctrl
      self.magnitude = min(100.0,math.sqrt(math.pow(self.reqmotorspeed,2.0) + math.pow(self.reqsteering,2.0)))
      self.myAngle = math.atan2(self.reqmotorspeed,self.reqsteering)
      # If motorctrl is 1, then translate into precise speed and direction up to 10mph
      if (self.motorctrl != 1.0) :
         # Make 1mph the maximum speed and approximate direction to forward, backward or spin
         self.magnitude = self.magnitude / 10
         self.myAngle = round(self.myAngle / (math.pi/4.0))*math.pi/4.0
      self.myAngle = self.myAngle - (math.pi/4.0)
      if self.name == "left" :
         self.targetspeed = self.magnitude * math.cos(self.myAngle)
      elif self.name == "right" :
         self.targetspeed = self.magnitude * math.sin(self.myAngle)
      else :
         print "Unknown motor"
         self.targetspeed = 0
      return self.targetspeed

   def getActualSpeed(self) :
      self.clicks = 0
      if not sim :
         if self.name == "left" :
            self.clicks = rc.ReadSpeedM1(rc_address)
         elif self.name == "right" :
            self.clicks = rc.ReadSpeedM2(rc_address)
         else:
            print "Unknown motor"
            self.speed = 0
         self.speed = int(self.clicks[1] / self.QPPS)
      else:
         self.speed = self.target
      print "Actual: " + str(self.name) + " at " + str(self.speed)
      return self.speed

   def setTargetSpeed(self, target) :
      if target >= -100 and target <= 100 :
         self.target = int(target)

   def setMotorSpeed(self) :
      if not sim :
         self.click_speed = int(self.QPPS * self.target)
         self.distance = int(abs(self.target * self.QPPS / 4))
         print "Command: " + str(self.name) + " set to " + str(self.click_speed)
         if self.name == "left" :
            if self.target == 0 :
               rc.SpeedM1(rc_address,0)
            else :
               rc.SpeedM1(rc_address,self.click_speed)
         elif self.name == "right" :
            if self.target == 0 :
               rc.SpeedM2(rc_address,0)
            else :
              rc.SpeedM2(rc_address,self.click_speed)
         else :
            print "Unknown motor"

class K9 :
   def __init__(self) :
      print "K9 object initialising"
      # Create names for each PWM channel
      self.pwm_eyes = 0
      self.pwm_hover = 1
      self.pwm_screen = 2
      self.pwm_lights = 3
      # Set initial values for k9
      self.lights = 100
      self.eyes = 3
      self.hover = 0
      self.screen = 100
      self.motorctrl = 0
      # Create two motor objects
      self.leftMotor = Motor("left",m1_qpps)
      self.rightMotor = Motor("right",m2_qpps)
      if not sim :
         # Initialise the PWM device using the default address
         # This is the Adafruit servo control device that makes the tail,
         # neck and ears move; it also is used to turn control the various
         # lights and devices such as the eye and hover lights and the
         # side screen using MOSFETS
         print "Initialising servo driver state..."
         self.pwm = Adafruit_PCA9685.PCA9685()
         print "pwm object created"
         self.pwm.set_pwm_freq(100)  # Set frequency to 100 Hz
         print "frequency set to 100Hz"
         self.set_k9_pwm(self.pwm_eyes,self.eyes)
         self.set_k9_pwm(self.pwm_hover,self.hover)
         self.set_k9_pwm(self.pwm_screen,self.screen)
         self.set_k9_pwm(self.pwm_lights,self.lights)
         print "All servo driver initial state set..."

   def set_k9_pwm(self,channel, brightness) :
      self.channel = channel
      self.brightness = brightness
      self.channel = int(self.channel)
      self.brightness = int(self.brightness * 40.95)
      print "Setting channel " + str(self.channel) + " to " + str(self.brightness)
      self.pwm.set_pwm(0,self.channel,self.brightness)
      print "Channel " + str(self.channel) + "set to " + str(self.brightness)

   def getStatusInfo(self) :
      # retrieves status of motors and lights
      # lights are part of the k9 state object anyway
      self.result = []
      self.left = self.leftMotor.getActualSpeed()
      self.right = self.rightMotor.getActualSpeed()
      if sim :
          self.main_volt = float(random.uniform(12,28))
          self.brain_volt = float(random.uniform(10,13))
          self.currents = [100.0,random.uniform(100,500),random.uniform(100,500)]
          self.temp = float(random.uniform(20,85))
      else :
          self.main_volt = float(rc.ReadMainBatteryVoltage(rc_address)[1])/10.0
          self.brain_volt = float(rc.ReadLogicBatteryVoltage(rc_address)[1])/10.0
          self.currents = rc.ReadCurrents(rc_address)
          self.temp = float(rc.ReadTemp(rc_address)[1])/10.0
      # Convert currents tuple in mAs to Amps
      self.m1current = float(self.currents[1]/100.0)
      self.m2current = float(self.currents[2]/100.0)
      result = json.dumps({"type":"status","command":"update","left": self.left,"right": self.right,"lights": self.lights,"eyes": self.eyes,"hover": self.hover,"screen": self.screen, "motorctrl": self.motorctrl, "main_volt": self.main_volt, "brain_volt": self.brain_volt, "motor_l_amp": self.m1current, "motor_r_amp": self.m2current, "temp": self.temp }, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=(',', ': '), encoding="utf-8", default=None, sort_keys=False)
      return result

# manages the ws socket connection from this Controller to local node-RED server
class K9PythonController(WebSocketClient) :

   def opened(self) :
      print "K9 Python Controller connected to node-RED server"
      self.k9 = K9()
      #self.timeout = Timer (50, self.closed(None,None) )
      #self.timeout.start()

   def closed(self, code, reason=None) :
      print "K9 Python Controller disconnected from node-RED server: ", code, reason
      self.k9.leftMotor.setTargetSpeed(0)
      self.k9.rightMotor.setTargetSpeed(0)
      self.k9.leftMotor.setMotorSpeed()
      self.k9.rightMotor.setMotorSpeed()
      #PBR.SetMotor1(0)
      #PBR.SetMotor2(0)
      # browser commands with type 'navigation' are automatically routed by node-RED to this socket
      # the navigation 'alive' command (basically a heartbeat)
      # is sent automatically by the browser and relayed via node-RED.
      # On receiving the heartbeat message, from node-RED this controller responds to the same socket
      # with the status of K9 as determined by this python program.  node-RED can then
      # forward the status string to the browser to display to the user
      # This round trip should provide a reliable indication to the end user that
      # communications between the browser, node-RED and the motors are working as expected

   def received_message(self, message) :
      self.message = message
      self.message = str(self.message) # turn message into JSON formatted string
      self.driveinfo = []
      self.driveinfo = json.loads(self.message) # parse JSON message string
      if self.driveinfo["type"] == "navigation":
         # navigation command received
         if self.driveinfo["object"] == "browser":
            # heartbeat received from browser
            self.message = self.k9.getStatusInfo()    # get K9 status information
            self.send(self.message)                   # send current status information to the node-RED websocket
            # print "Status: " + str(self.message)
         elif self.driveinfo["object"] == "motorctrl":
            # toggle fine or coarse grained motor control
            if self.driveinfo["value"] == "on":
               self.k9.motorctrl = 1.0
            else:
               self.k9.motorctrl = 0.0
         elif self.driveinfo["object"] == "motors":
            # change the motor speeds
            self.motorspeed = float(self.driveinfo["motorspeed"])
            self.steering = float(self.driveinfo["steering"])
            self.leftTarget = self.k9.leftMotor.calculateTargetSpeed(self.motorspeed, self.steering,self.k9.motorctrl)
            self.rightTarget = self.k9.rightMotor.calculateTargetSpeed(self.motorspeed, self.steering,self.k9.motorctrl)
            # Calculate the magnitude of the movement calculated (0-100)
            # and make that the value of the hover brightness
            self.k9.hover = min(((abs(self.leftTarget) + abs(self.rightTarget))/2),100)
            # set the hover lights brightness
            self.k9.set_k9_pwm(self.k9.pwm_hover,self.k9.hover)
            # set the motor speeds
            self.k9.leftMotor.setTargetSpeed(self.leftTarget)
            self.k9.rightMotor.setTargetSpeed(self.rightTarget)
            self.k9.leftMotor.setMotorSpeed()
            self.k9.rightMotor.setMotorSpeed()
         else:
            # command could not be interpreted
            print "Command object not understood: " + str(self.driveinfo)
      else:
         # not a navigation command
         print "Illegal command received: " + str(self.driveinfo)

# Wait for node-RED server to become active
if not sim :
   time.sleep(30)

try:
   ws = K9PythonController(address)
   ws.connect()
   ws.run_forever()
except KeyboardInterrupt:
   if not sim :
      # reset motors to zero
      ws.k9.leftMotor.setTargetSpeed(0)
      ws.k9.rightMotor.setTargetSpeed(0)
      ws.k9.leftMotor.setMotorSpeed()
      ws.k9.rightMotor.setMotorSpeed()
      GPIO.cleanup()
   ws.close()
   print "Exiting controller after cleanup."
