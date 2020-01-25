#***Before using this example the motor/controller combination must be
#***tuned and the settings saved to the Roboclaw using IonMotion.
#***The Min and Max Positions must be at least 0 and 50000

import time
from roboclaw import Roboclaw

#Windows comport name
rc = Roboclaw("COM3",115200)
#Linux comport name
#rc = Roboclaw("/dev/ttyACM0",115200)

def displayspeed():
	enc1 = rc.ReadEncM1(address)
	enc2 = rc.ReadEncM2(address)
	speed1 = rc.ReadSpeedM1(address)
	speed2 = rc.ReadSpeedM2(address)

	print("Encoder1:"),
	if(enc1[0]==1):
		print enc1[1],
		print format(enc1[2],'02x'),
	else:
		print "failed",
	print "Encoder2:",
	if(enc2[0]==1):
		print enc2[1],
		print format(enc2[2],'02x'),
	else:
		print "failed " ,
	print "Speed1:",
	if(speed1[0]):
		print speed1[1],
	else:
		print "failed",
	print("Speed2:"),
	if(speed2[0]):
		print speed2[1]
	else:
		print "failed "

rc.Open()
address = 0x80

version = rc.ReadVersion(address)
if version[0]==False:
	print "GETVERSION Failed"
else:
	print repr(version[1])

while(1):
	rc.SpeedDistanceM1(address,12000,48000,1)
	rc.SpeedDistanceM2(address,-12000,48000,1)
	buffers = (0,0,0)
	while(buffers[1]!=0x80 and buffers[2]!=0x80):	#Loop until distance command has completed
		displayspeed();
		buffers = rc.ReadBuffers(address);
  
	time.sleep(2)

	rc.SpeedDistanceM1(address,-12000,48000,1)
	rc.SpeedDistanceM2(address,12000,48000,1)
	buffers = (0,0,0)
	while(buffers[1]!=0x80 and buffers[2]!=0x80):	#Loop until distance command has completed
		displayspeed()
		buffers = rc.ReadBuffers(address)
  
	time.sleep(2);  #When no second command is given the motors will automatically slow down to 0 which takes 1 second

	rc.SpeedDistanceM1(address,12000,48000,1)
	rc.SpeedDistanceM2(address,-12000,48000,1)
	rc.SpeedDistanceM1(address,-12000,48000,0)
	rc.SpeedDistanceM2(address,12000,48000,0)
	rc.SpeedDistanceM1(address,0,48000,0)
	rc.SpeedDistanceM2(address,0,48000,0)
	buffers = (0,0,0)
	while(buffers[1]!=0x80 and buffers[2]!=0x80):	#Loop until distance command has completed
		displayspeed()
		buffers = rc.ReadBuffers(address)
  
	time.sleep(1)
