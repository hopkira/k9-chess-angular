# ===========================================================================
# Simple routine to make K9's tail wag up and down
# ===========================================================================
# Import the PCA9685 module.

import time
import board
import busio
import adafruit_pca9685
i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)
pca.frequency = 60

pca.channels[5].duty_cycle = 5601	# tail left
# pwm.set_pwm(5, 0, 350)	# tail centre horizontally

count= 0
while count < 4:
    pca.channels[4].duty_cycle = 5921	# tail left
    # pwm.set_pwm(4, 0, 370)	# tail up
    time.sleep(0.25)
    pca.channels[4].duty_cycle = 4321	# tail left
    # pwm.set_pwm(4, 0, 270)	# tail down
    time.sleep(0.25)
    count +=1
pca.channels[4].duty_cycle = 5601	# tail left
# pwm.set_pwm(4, 0, 350)	# tail centre

# 270 -> 4321
# 320 -> 5121
# 325 -> 5201
# 350 -> 5601
# 370 -> 5921
# 440 -> 7042