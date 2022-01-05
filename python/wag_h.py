 # ===========================================================================
 # Simple routine to make K9's tail wag left and right
 # ===========================================================================
# Import the PCA9685 module.
import time
import board
import busio
import adafruit_pca9685
i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)
pca.frequency = 60

pca.channels[4].duty_cycle = 5121 # centre tail vertically

count= 0
while count < 4:
    pca.channels[5].duty_cycle = 5201	# tail left
    # pwm.set_pwm(5, 0, 325)	# tail left
    time.sleep(0.25)
    pca.channels[5].duty_cycle = 7042	# tail right
    # pwm.set_pwm(5, 0, 440)	# tail right
    time.sleep(0.25)
    count +=1
# pwm.set_pwm(5, 0, 350)	# tail centre4
pca.channels[5].duty_cycle = 5601	# tail centre

#import Adafruit_PCA9685
#import time
#pwm = Adafruit_PCA9685.PCA9685()
#pwm.set_pwm_freq(60)		# set frequency to 60 Hz
# origianlly out of 4095, now 65535
# 320 -> 5121
# 325 -> 5201
# 350 -> 5601
# 440 -> 7042