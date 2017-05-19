#
# Initialise PID values on motor controller
#
import time    # enable sleep function
from roboclaw import Roboclaw # enabling Roboclaw
rc = Roboclaw("/dev/roboclaw",115200)
rc.Open()
rc_address = 0x80
version = rc.ReadVersion(rc_address)
if version[0]==False:
   print "Roboclaw get version failed, exiting..."
   sys.exit()
else:
   print repr(version[1])
   rc.SetM1VelocityPID(rc_address,3000,300,0,708)
   rc.SetM2VelocityPID(rc_address,3000,300,0,720)
   WriteNVM(self,address)
   time.sleep(30)
   print "Motor controller PID values intialised, exiting..."
