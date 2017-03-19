#
# K9 Python Controller
#
# authored by Richard Hopkins, March 2017
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
# and send a message to the PicoBorg Reverse to move K9.
#
import sys		# allows for command line to be interpreted
import json		# enables creation of JSON strings
import os		# enables access to environment variables
import math		# import maths operations
import random	# import random numbers
import time 	# enable sleep function

sys.path.append('/home/pi/picoborgrev') # include home directory in path
sys.path.append('/home/pi')

from ws4py.client.threadedclient import WebSocketClient #enabling web sockets

sim = False # by default run as a real motor controller

# sim is a program wide flag to allow the program to run without the PiBorg Reverse
# and without access to the Raspberry Pi GPIO ports
# this can be enabled by appending the word "test" to the command line

if ( len(sys.argv) > 1 ) :
	if ( sys.argv[1] == "test" ) :
		sim = True
		print "Executing in simulation mode" # let the user know they are in sim mode

# Initialise PicoBorg Reverse if not in simulation mode
if not sim :
	from k9secrets import K9PyContWS # gets the node-RED websocket address 
	address = K9PyContWS
	import PicoBorgRev
	PBR = PicoBorgRev.PicoBorgRev()
	PBR.Init()
	PBR.ResetEpo()
	PBR.SetCommsFailsafe(True) # ensures motor stops if communications do
	import RPi.GPIO as GPIO # enables manipulation of GPIO ports
	GPIO.setmode(GPIO.BOARD) # use board numbers rather than BCM numbers
	GPIO.setwarnings(False) # remove duplication warnings
	chan_list = [11,13]    # GPIO channels to initialise and use
	GPIO.setup(chan_list, GPIO.IN) # set GPIO to low at initialise
else :
	address = "ws://127.0.0.1:1880/ws"

class PID :
	def __init__(self) :
		print "PID Object instantiated"
		self.iGain = 0
		self.pGain = 0
		self.dGain = 0
		self.iStateMax = 0
		self.iStateMin = 0
		self.iState = 0
		self.lastError = 0
		
	def setPIDGain(self, iGain, pGain, dGain, iStateMin, iStateMax) :
		self.iGain = iGain
		self.pGain = pGain
		self.dGain = dGain
		self.iStateMin = iStateMin
		self.iStateMax = iStateMax
		self.iState = 0
		self.lastError = 0

	def getPID(self, requested, actual):
		self.requested = requested
		self.actual = actual
		self.error = self.requested - self.actual
		# calculate proportional term
		self.pTerm = self.error
		# calculate integral term
		self.iState = self.iState + self.error
		if self.iState > self.iStateMax :
			self.iState = iStateMax
		if self.iState < self.iStateMin :
			self.iState = self.iStateMin
		# calculate derivative term
		self.dTerm = self.error + (self.error - self.lastError)
		self.lastError = self.error
		self.PID = (self.pTerm * self.pGain) + (self.iState * self.iGain) + (self.dTerm * self.dGain)
		return self.PID

class TimeSeries :
	def __init__(self, size):
		print "Time series object instantiated: " + str(size)
		self.size = size
		if self.size < 2 :
			print "ValueError : TimeSeries: must have at least two points in time series"
			raise ValueError()
		self.records = []
	
	def recordValue(self,time,value):
		self.records.insert(0,[time,value])
		if len(self.records) > self.size :
	 		self.records.pop()
	 		# print "Overflowed queue"
	
	def getRateofChange(self):
		if len(self.records)<2 :
			print "TimeSeries: insufficient data to calculate rate of change"
			return 0
		else :
			self.roc = 0
			# print "Size: " + str(len(self.records))
			self.start_time = float(self.records[len(self.records)-1][0])
			self.end_time = float(self.records[0][0])
			self.duration = self.end_time-self.start_time
			# print "Duration: " + str(self.end_time-self.start_time) 
			for self.index in range(len(self.records)-1):
				self.start_time = float(self.records[self.index+1][0])
				self.end_time = float(self.records[self.index][0])
				self.start_value = float(self.records[self.index+1][1])
				self.end_value = float(self.records[self.index][1])
				self.time_delta = self.end_time - self.start_time
				self.avg_value = (self.start_value + self.end_value) / 2
				self.delta_roc = self.avg_value/self.time_delta
				self.roc = self.roc + self.delta_roc*(self.time_delta/self.duration)
				# print "Time delta = " + str(self.time_delta)
				# print "Avg value = " + str(self.avg_value)
				# print "Rate of change = " + str(self.roc)
			return self.roc

class Motor :
	def __init__(self,name) :
		self.name = name
		print str(name) + " motor object instantiated."
		self.target = 0.0
		self.speed = 0.0
		self.pid = PID()
		self.t = TimeSeries(3)
		
	def calculateTargetSpeed(reqmotorspeed,reqsteering) :
		self.reqmotorspeed = reqmotorspeed
		self.reqsteering = reqsteering
		self.magnitude = min(100,math.sqrt(math.pow(self.reqmotorspeed,2) + math.pow(self.reqsteering,2)))
		self.myAngle = math.atan2(self.reqmotorspeed,self.reqsteering)
		self.myAngle = self.myAngle - (math.pi/4)
		if self.name == "left" :
			self.targetspeed = round(self.magnitude * math.cos(self.myAngle),0)
		elif self.name == "right" :
			self.targetspeed = round(self.magnitude * math.sin(self.myAngle),0)
		else :
			print "Unknown motor"
			self.targetspeed = 0
		return self.targetspeed
		
	def getActualSpeed(self) :
		if not sim :
			self.actualclicks = self.t.getRateofChange()
			self.speed = self.convertClickstoSpeed(self.actualclicks)
		else :
			self.speed = self.target
		return self.speed
		
	def	convertClickstoSpeed(self,clicks) :
		self.clicks = clicks
		self.convertedClicks = self.clicks * 25
		return self.convertedClicks
	
	def setTargetSpeed(self, target) :
		if target > -100 and target < 100 :
			self.target = target
			
	def setMotorSpeed() :
		self.adjustedTarget = self.target + self.pid.getPID()
		if not sim :
			if self.name == "left" :
				PBR.SetMotor1(self.adjustedTarget/100)
			elif self.name == "right" :
				PBR.SetMotor2(self.adjustedTarget/100)
			else :
				print "Unknown motor"
	
class K9 :
	def __init__(self) :
		print "K9 object instantiated"
		self.lights = 0.0
		self.eyes = 0.0
		self.hover = 0.0
		self.screen = 0.0
		self.leftMotor = Motor("left")
		self.rightMotor = Motor("right")
		
	def getStatusInfo() :
		self.result = []
		self.left = leftMotor.getActualSpeed()
		self.right = rightMotor.getActualSpeed()
		# retrieves status of motors and lights
		if not sim :
			self.lights = GPIO.input(11)
			self.eyes = GPIO.input(13)
			# *** fix need status of hover lights and screen ****
		else :
			if  (random.randint(1, 100)) == 10:
				self.lights = 1-self.lights
			if  (random.randint(1, 100)) == 10:
				self.eyes = 1-self.eyes
			if  (random.randint(1, 100)) == 10:
				self.hover = 1-self.hover
			if  (random.randint(1, 100)) == 10:
				self.screen = 1-self.screen
		result = json.dumps({"type":"status","command":"update","left": left,"right": right,"lights": lights,"eyes": eyes,"hover": hover,"screen": screen}, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=(',', ': '), encoding="utf-8", default=None, sort_keys=False)
		return result

# manages the ws socket connection from this Controller to local node-RED server
class K9PythonController(WebSocketClient) :
		
	def opened(self) :
		self.k9 = K9()
		print "K9 Python Controller connected to node-RED server"
		
	def closed(self, code, reason=None) :
		if not sim :
			self.k9.leftMotor.setTargetSpeed(0.0)
			self.k9.rightMotor.setTargetSpeed(0.0)
			#PBR.SetMotor1(0)
			#PBR.SetMotor2(0)
		print "K9 Python Controller disconnected from node-RED server", code, reason
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
		#global motorspeed
		#global steering
		#global leftMotor
		#global rightMotor
		self.message = str(self.message) # turn message into JSON formatted string
		self.driveinfo = []
		self.driveinfo = json.loads(self.message) # parse JSON message string
		if self.driveinfo["type"] == "navigation":
			# navigation command received
			if self.driveinfo["object"] == "browser":
				# heartbeat received from browser, so set motor speeds
				# this will reset the timeout on the motors
				self.k9.leftMotor.setMotorSpeed()
				self.k9.rightMotor.setMotorSpeed()
				self.message = self.k9.getStatusInfo()		# get K9 status information
				self.send(self.message)					# send current status information to the node-RED websocket
				print "Status: " + str(self.message)
			elif self.driveinfo["object"] == "motors":
				# change the motor speeds
				self.motorspeed = float(self.driveinfo["motorspeed"])
				self.steering = float(self.driveinfo["steering"])
				self.leftTarget = self.k9.leftMotor.calculateTargetSpeed(self.motorspeed, self.steering)
				self.rightTarget = self.k9.rightMotor.calculateTargetSpeed(self.motorspeed, self.steering)
				self.k9.leftMotor.setTargetSpeed(leftTarget)
				self.k9.rightMotor.setTargetSpeed(rightTarget)
				self.k9.leftMotor.setMotorSpeed()
				self.k9.rightMotor.setMotorSpeed()
			elif self.driveinfo["object"] == "encoders":
				# refresh observed speed
				print "Encoder message received"
				self.leftclicks = float(self.driveinfo["left"])
				self.rightclicks = float(self.driveinfo["right"])
				self.time = float(self.driveinfo["time"])
				self.k9.leftMotor.t.recordValue(self.time,self.leftclicks)
				self.k9.rightMotor.t.recordValue(self.time,self.rightclicks)
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
		ws.k9.leftMotor.setTargetSpeed(0.0)
		ws.k9.rightMotor.setTargetSpeed(0.0)
		ws.k9.leftMotor.setMotorSpeed()
		ws.k9.rightMotor.setMotorSpeed()
		GPIO.cleanup()
	ws.close()
	print "Exiting controller after cleanup."
