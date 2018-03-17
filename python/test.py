import math

from roboclaw import Roboclaw
rc = Roboclaw("/dev/roboclaw",115200)
rc.Open()
version = rc.ReadVersion(address)
if version[0]==False:
	print "GETVERSION Failed"
else:
	print repr(version[1])
address = 0x80
nvm=[0,0,0]
rc.ReadNVM(address)
print str(nvm)
clicks = 300
click_vel = 30
ACCELERATION = 10
rc.SpeedAccelDistanceM1M2(address=address,accel=ACCELERATION,speed1=click_vel,distance1=int(abs(clicks/2)),speed2=int(click_vel),distance2=int(abs(clicks/2)),buffer=1)
rc.SpeedAccelDistanceM1M2(address=address,accel=ACCELERATION,speed1=0,distance1=int(abs(clicks/2)),speed2=0,distance2=int(abs(clicks/2)),buffer=0)
buffers = (0,0,0)
while (buffers[1]!=0x80 and buffers[2]!=0x80):
    buffers = rc.ReadBuffers(address);
    print "Waiting"
print "Stopping"
rc.SpeedAccelDistanceM1M2(address=address,accel=ACCELERATION,speed1=0,distance1=0,speed2=0,distance2=0,buffer=1)
print "Stop done"
