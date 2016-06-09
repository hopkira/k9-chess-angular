#
# K9 Python Controller
#
# authored by Richard Hopkins, February 2016
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
import sys   # allows for command line to be interpreted
import json  # enables creation of JSON strings

import math # import maths operations
import random # import random numbers

from ws4py.client.threadedclient import WebSocketClient #enabling web sockets

sim = False # by default run as a real motor controller

# Global variables for K9 state

steering = 0
motorspeed = 0
leftMotor = 0
rightMotor = 0
lights = 0
eyes = 0
hover = 0
screen = 0

# sim is a program wide flag to allow the program to run without the PiBorg Reverse
# and without access to the Raspberry Pi GPIO ports
# this can be enabled by appending the word "test" to the command line

if ( len(sys.argv) > 1 ) :
    if ( sys.argv[1] == "test" ) :
       sim = True
       print "Executing in simulation mode" # let the user know they are in sim mode

# Initialise PicoBorg Reverse if not in simulation mode
if not sim :
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

# retrieves current K9 status and populates it
# into a JSON status string and
# updates a set of global variables
def getStatusInfo() :
	result = []
	global lights
	global eyes
	global hover
	global screen
	left = 0
	right = 0
	# retrieves status of motors and lights
	if not sim :
	    left = PBR.GetMotor1()
	    right = PBR.GetMotor2()
	    # retrieves status of lights:
	    lights = GPIO.input(11)
	    eyes = GPIO.input(13)
	    # *** fix need status of hover lights and screen ****
	else:
	    left = leftMotor
	    right = rightMotor
	    if  (random.randint(1, 100)) == 10:
	      lights = 1-lights
	    if  (random.randint(1, 100)) == 10:
	      eyes = 1-eyes
	    if  (random.randint(1, 100)) == 10:
	      hover = 1-hover
	    if  (random.randint(1, 100)) == 10:
	      screen = 1-screen
	result = json.dumps({"type":"status","command":"update","left": left,"right": right,"lights": lights,"eyes": eyes,"hover": hover,"screen": screen}, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=(',', ': '), encoding="utf-8", default=None, sort_keys=False)
	return result

# manages the ws socket connection from this Controller to local node-RED server
class K9PythonController(WebSocketClient) :
    def opened(self) :
        print "K9 Python Controller connected to node-RED server"
    def closed(self, code, reason=None) :
        if not sim :
            PBR.SetMotor1(0)
            PBR.SetMotor2(0)
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
        global motorspeed
        global steering
        global leftMotor
        global rightMotor
        message = str(message) # turn message into JSON formatted string
        driveinfo = []
        driveinfo = json.loads(message) # parse JSON message string
        commandtype = driveinfo["type"]
        if driveinfo["type"] == "navigation":
            # navigation command received
            if driveinfo["object"] == "browser":
                setMotorSpeed(leftMotor, rightMotor) # this will reset the failsafe
                m = getStatusInfo()		# get K9 status information
                self.send(m)			# send current status information to the node-RED websocket
                print str(m)
            elif driveinfo["object"] == "motors":
                # change the motor speeds
                motorspeed = float(driveinfo["motorspeed"])
                steering = float(driveinfo["steering"])
                calculateMotorSpeed(motorspeed,steering)
                setMotorSpeed(motorspeed, steering) # this will reset the failsafe
            else:
                # command could not be interpreted
                print "Command not understood: " + driveinfo
        else:
            # not a navigation command
            print "Illegal command received: " + driveinfo
        return
#
# setMotorSpeed will set the speed of the two motors
# detailed explanation of the below code - with pictures here
# http://k9-build.blogspot.co.uk/2016/02/taking-pythagoras-for-spin.html
#
def setMotorSpeed(reqmotorspeed,reqsteering) :
    if not sim :
            PBR.SetMotor1(reqmotorspeed)		# set actual motor speed
            PBR.SetMotor2(reqsteering)		# set actual motor speed
    return

def calculateMotorSpeed(reqmotorspeed,reqsteering) :
    global leftMotor
    global rightMotor
    magnitude = min(100,math.sqrt(math.pow(reqmotorspeed,2) + math.pow(reqsteering,2)))
    myAngle = math.atan2(reqmotorspeed,reqsteering)
    myAngle = myAngle - (math.pi/4)
    leftMotor = round(magnitude * math.cos(myAngle),0)
    rightMotor = round(magnitude * math.sin(myAngle),0)
    print "Motorspeed: " + str(int(reqmotorspeed)) + " Steering: " + str(int(reqsteering))
    print "Left motor: " + str(int(leftMotor)) + " Right motor: " + str(int(rightMotor))
    return

try:
     ws = K9PythonController('ws://127.0.0.1:1880/admin/ws/motors')
     ws.connect()
     ws.run_forever()
except KeyboardInterrupt:
     if not sim :
         PBR.SetMotor1(0)
         PBR.SetMotor2(0)
         GPIO.cleanup()
     ws.close()
     print "Exiting controller after cleanup."
