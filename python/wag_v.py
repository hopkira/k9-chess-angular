from Adafruit_PWM_Servo_Driver import PWM # enabling servo driver 
import time
 # ===========================================================================  
 # Simple routine to make K9's tail wag up and down 
 # =========================================================================== 

pwm = PWM(0x40)			# initialise the PWM device using the default address
pwm.setPWMFreq(60)		# set frequency to 60 Hz

count= 0
while count < 4:
	pwm.setPWM(4, 0, 270)	# tail down
	time.sleep(0.25)
	pwm.setPWM(4, 0, 370)	# tail up
	time.sleep(0.25)
	count +=1
pwm.setPWM(4, 0, 270)	# tail up
