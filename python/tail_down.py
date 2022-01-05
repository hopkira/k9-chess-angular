 # ===========================================================================
 # Simple routine to make K9's tail go down
 # ===========================================================================

import time
import board
import busio
import adafruit_pca9685
i2c = busio.I2C(board.SCL, board.SDA)
pca = adafruit_pca9685.PCA9685(i2c)
pca.frequency = 60

pca.channels[4].duty_cycle = 5921	# tail down

# 270 -> 4321
# 320 -> 5121
# 325 -> 5201
# 350 -> 5601
# 370 -> 5921
# 440 -> 7042