from Adafruit_PWM_Servo_Driver import PWM # enabling servo driver 

 # ===========================================================================  
 # Simple routine to make K9's tail move down 
 # =========================================================================== 

pwm = PWM(0x40)			# initialise the PWM device using the default address
pwm.setPWMFreq(60)		# set frequency to 60 Hz

pwm.setPWM(4, 0, 370)	# tail down
