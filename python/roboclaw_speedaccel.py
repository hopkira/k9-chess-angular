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
	rc.SpeedAccelM1(address,12000,12000)
	rc.SpeedAccelM2(address,12000,-12000)
	for i in range(0,200):
		displayspeed()
		time.sleep(0.01)

	rc.SpeedAccelM1(address,12000,-12000)
	rc.SpeedAccelM2(address,12000,12000)
	for i in range(0,200):
		displayspeed()
		time.sleep(0.01)
  