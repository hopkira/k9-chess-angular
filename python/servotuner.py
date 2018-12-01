import sys   # allows for command line to be interpreted
       
servoMin = 150			# min pulse length out of 4096
servoMax = 600			# max pulse length out of 4096
servo = 0				# default servo
value = 375				# default value for servo

if ( len(sys.argv) > 1 ) :
	servo = int(sys.argv[1])
	value = int(sys.argv[2])
	
print 'Servo: ' + str(servo) + ' Value: ' + str(value)

from Adafruit_PWM_Servo_Driver import PWM # enabling servo driver 

pwm = PWM(0x40)			# initialise the PWM device using the default address
pwm.setPWMFreq(60)		# set frequency to 60 Hz

pwm.setPWM(servo, 0, value)	# set motor speed
