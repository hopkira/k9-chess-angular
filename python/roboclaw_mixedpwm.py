import time
from roboclaw import Roboclaw

#Windows comport name
rc = Roboclaw("COM9",115200)
#Linux comport name
#rc = Roboclaw("/dev/ttyACM0",115200)

rc.Open()
address = 0x80

rc.ForwardMixed(address, 0)
rc.TurnRightMixed(address, 0)

while(1):
	rc.ForwardMixed(address, 32)
	time.sleep(2)
	rc.BackwardMixed(address, 32)
	time.sleep(2)
	rc.TurnRightMixed(address, 32)
	time.sleep(2)
	rc.TurnLeftMixed(address, 32)
	time.sleep(2)
	rc.ForwardMixed(address, 0)
	rc.TurnRightMixed(address, 32)
	time.sleep(2)
	rc.TurnLeftMixed(address, 32)
	time.sleep(2)
	rc.TurnRightMixed(address, 0)
	time.sleep(2)
