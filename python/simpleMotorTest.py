import math
from roboclaw import Roboclaw
address = 0x80
rc = Roboclaw("/dev/roboclaw",115200)
rc.Open()
version = rc.ReadVersion(address)
if version[0]==False:
	print "GETVERSION Failed"
else:
	print repr(version[1])
rc.SetM1VelocityPID(address,3000,300,0,708)
rc.SetM2VelocityPID(address,3000,300,0,720)
clicks = 5000
click_vel = 300
ACCELERATION = 30

while(1):
	rc.ForwardM1(address,32)	#1/4 power forward
	rc.BackwardM2(address,32)	#1/4 power backward
	time.sleep(2)

	rc.BackwardM1(address,32)	#1/4 power backward
	rc.ForwardM2(address,32)	#1/4 power forward
	time.sleep(2)

	rc.BackwardM1(address,0)	#Stopped
	rc.ForwardM2(address,0)		#Stopped
	time.sleep(2)

	m1duty = 16
	m2duty = -16
	rc.ForwardBackwardM1(address,64+m1duty)	#1/4 power forward
	rc.ForwardBackwardM2(address,64+m2duty)	#1/4 power backward
	time.sleep(2)

	m1duty = -16
	m2duty = 16
	rc.ForwardBackwardM1(address,64+m1duty)	#1/4 power backward
	rc.ForwardBackwardM2(address,64+m2duty)	#1/4 power forward
	time.sleep(2)

	rc.ForwardBackwardM1(address,64)	#Stopped
	rc.ForwardBackwardM2(address,64)	#Stopped
	time.sleep(2)
