# Import the PCA9685 module.
import Adafruit_PCA9685
import time
 # ===========================================================================
 # Simple routine to make K9's tail wag left and right
 # ===========================================================================
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)		# set frequency to 60 Hz

pwm.set_pwm(4, 0, 320)	# centre tail vertically

count= 0
while count < 4:
    pwm.set_pwm(5, 0, 325)	# tail left
    time.sleep(0.25)
    pwm.set_pwm(5, 0, 440)	# tail right
    time.sleep(0.25)
    count +=1
pwm.set_pwm(5, 0, 350)	# tail centre
