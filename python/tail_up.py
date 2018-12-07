# Import the PCA9685 module.
import Adafruit_PCA9685
import time
 # ===========================================================================
 # Simple routine to make K9's tail go up
 # ===========================================================================
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)		# set frequency to 60 Hz

pwm.set_pwm(4, 0, 270)	# tail up
