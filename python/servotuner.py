# Import the PCA9685 module.
import Adafruit_PCA9685
import time
 # ===========================================================================
 # Simple routine to make K9's tail go up
 # ===========================================================================
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)		# set frequency to 60 Hz

import sys   # allows for command line to be interpreted

servoMin = 150			# min pulse length out of 4096
servoMax = 600			# max pulse length out of 4096
servo = 0				# default servo
value = 375				# default value for servo

if ( len(sys.argv) > 1 ) :
    servo = int(sys.argv[1])
    value = int(sys.argv[2])

print 'Servo: ' + str(servo) + ' Value: ' + str(value)

pwm.set_pwm(servo, 0, value)	# set motor speed
